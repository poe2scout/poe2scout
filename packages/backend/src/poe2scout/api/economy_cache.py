import asyncio
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
import logging
import random
from typing import Generic, List, TypeVar

from pydantic import BaseModel
from poe2scout.db.repositories import (
    currency_item_repository,
    league_repository,
    price_log_repository,
    unique_item_repository,
)
from poe2scout.db.repositories.models import (
    CurrencyItemExtended,
    PriceLogEntry,
    UniqueItemExtended,
)
from poe2scout.db.repositories.price_log_repository.get_item_daily_stats import (
    GetItemDailyStatsDto,
)
from poe2scout.services.pricing import (
    convert_price_log_matrix_from_base,
    convert_prices_from_base,
)

T = TypeVar("T")

logger = logging.getLogger(__name__)


def get_daily_stat_dates():
    current_date = datetime.now(tz=timezone.utc).date()
    return [current_date - timedelta(days=i) for i in range(7)]


def build_daily_stat_price_logs(
    item_ids: list[int],
    dates: list[date],
    daily_stats: list[GetItemDailyStatsDto],
) -> dict[int, list[PriceLogEntry | None]]:
    results: dict[int, list[PriceLogEntry | None]] = {
        item_id: [None] * len(dates) for item_id in item_ids
    }
    date_indices: dict[date, list[int]] = {}
    for index, stat_date in enumerate(dates):
        date_indices.setdefault(stat_date, []).append(index)

    for stat in daily_stats:
        if stat.item_id not in results:
            continue

        for date_index in date_indices.get(stat.day, []):
            results[stat.item_id][date_index] = PriceLogEntry(
                price=stat.avg_price,
                time=datetime.combine(stat.day, time.min),
                quantity=stat.volume,
            )

    return results


class CacheState(BaseModel, Generic[T]):
    value: List[T]
    expires: datetime


class CacheKey(BaseModel):
    category: str
    league_id: int
    realm_id: int
    game_id: int
    reference_currency: str

    class Config:
        frozen = True


class EconomyCache:
    CurrencyCache: dict[CacheKey, CacheState[CurrencyItemExtended]]
    UniqueCache: dict[CacheKey, CacheState[UniqueItemExtended]]

    CurrencyLocks: dict[CacheKey, asyncio.Lock]

    def __init__(self):
        self.CurrencyCache = {}
        self.UniqueCache = {}
        self.CurrencyLocks = defaultdict(asyncio.Lock)

    async def get_currency_page(
        self,
        league_id: int,
        realm_id: int,
        game_id: int,
        category: str,
        reference_currency: str,
        search: str,
    ) -> List[CurrencyItemExtended]:
        items: List[CurrencyItemExtended]
        cache_key = CacheKey(
            category=category, 
            league_id=league_id, 
            realm_id=realm_id,
            game_id=game_id,
            reference_currency=reference_currency
        )

        cache_entry = self.CurrencyCache.get(cache_key)
        if cache_entry and cache_entry.expires > datetime.now():
            logger.info(f"HitCache for {cache_key}")
            items = self.CurrencyCache[cache_key].value
        else:
            lock = self.CurrencyLocks[cache_key]

            async with lock:
                cache_entry = self.CurrencyCache.get(cache_key)
                if cache_entry and cache_entry.expires > datetime.now():
                    logger.info(f"HitCache (AfterLock) for {cache_key}")
                    items = cache_entry.value
                else:
                    logger.info(f"Cache empty for {cache_key}, fetching from DB.")
                    items = await self.fetch_currency_page(cache_key)

        if search:
            items = [item for item in items if item.text == search]

        return items

    async def get_unique_page(
        self,
        league_id: int,
        realm_id: int,
        game_id: int,
        category: str,
        reference_currency: str,
        search: str,
    ) -> List[UniqueItemExtended]:
        items: List[UniqueItemExtended]

        cache_key = CacheKey(
            category=category, 
            league_id=league_id, 
            realm_id=realm_id,
            game_id=game_id,
            reference_currency=reference_currency
        )
        if (
            self.UniqueCache.get(cache_key) is not None
            and self.UniqueCache[cache_key].expires > datetime.now()
        ):
            logger.info(f"HitCache for {cache_key}")
            items = self.UniqueCache[cache_key].value
        else:
            logger.info(f"Cache empty for {cache_key}")
            items = await self.fetch_unique_page(cache_key)
            self.UniqueCache[cache_key] = CacheState[UniqueItemExtended](
                value=items,
                expires=datetime.now() + timedelta(hours=1, minutes=random.randint(0, 15)),
            )
        if search != "":
            items = [item for item in items if item.name.lower() == search.lower()]

        return items

    async def fetch_unique_page(self, cache_key: CacheKey) -> List[UniqueItemExtended]:
        items_in_current_league, unique_items = await asyncio.gather(
            league_repository.get_items_in_current_league(
                cache_key.league_id,
                cache_key.realm_id,
            ),
            unique_item_repository.get_unique_items_by_category(cache_key.category),
        )
        items_in_current_league_set = set(items_in_current_league)

        unique_items = [
            uniqueItem
            for uniqueItem in unique_items
            if uniqueItem.item_id in items_in_current_league_set
        ]
        item_ids = [item.item_id for item in unique_items]

        if not item_ids:
            return []

        daily_stat_dates = get_daily_stat_dates()
        price_logs = build_daily_stat_price_logs(
            item_ids,
            daily_stat_dates,
            await price_log_repository.get_item_daily_stats(
                item_ids,
                cache_key.league_id,
                cache_key.realm_id,
                daily_stat_dates,
            ),
        )

        reference_currency_price = 1.0
        if cache_key.reference_currency:
            reference_currency_item = await currency_item_repository.get_currency_item(
                cache_key.reference_currency,
                cache_key.game_id,
            )
            if reference_currency_item is None:
                raise Exception()

            reference_currency_price = await price_log_repository.get_item_price(
                reference_currency_item.item_id,
                cache_key.league_id,
                cache_key.realm_id,
                None,
            )
            reference_currency_logs = build_daily_stat_price_logs(
                [reference_currency_item.item_id],
                daily_stat_dates,
                await price_log_repository.get_item_daily_stats(
                    [reference_currency_item.item_id],
                    cache_key.league_id,
                    cache_key.realm_id,
                    daily_stat_dates,
                ),
            )[reference_currency_item.item_id]
            price_logs = convert_price_log_matrix_from_base(
                price_logs,
                reference_currency_logs,
            )

        last_price = dict.fromkeys(item_ids, 0.0)

        prices = await price_log_repository.get_item_prices(
            item_ids, 
            cache_key.league_id,
            cache_key.realm_id
        )

        prices_lookup = {price.item_id: price for price in prices}
        converted_current_prices = convert_prices_from_base(
            {
                price.item_id: float(price.price)
                for price in prices_lookup.values()
            },
            reference_currency_price,
        )

        items = [
            UniqueItemExtended(**item.model_dump(), price_logs=price_logs[item.item_id])
            for item in unique_items
        ]

        for item in items:
            last_price[item.item_id] = converted_current_prices[item.item_id]

        items.sort(
            key=lambda item: (
                last_price[item.item_id] if item.item_id in last_price else 0
            ),
            reverse=True,
        )

        items = [
            UniqueItemExtended(
                **item.model_dump(exclude={"current_price", "current_quantity"}),
                current_price=last_price[item.item_id],
                current_quantity=prices_lookup[item.item_id].quantity,
            )
            for item in items
        ]

        return items

    async def fetch_currency_page(self, cache_key: CacheKey) -> List[CurrencyItemExtended]:
        items_in_current_league, currency_items = await asyncio.gather(
            league_repository.get_items_in_current_league(
                cache_key.league_id,
                cache_key.realm_id,
            ),
            currency_item_repository.get_currency_items_by_category(cache_key.category),
        )
        items_in_current_league_set = set(items_in_current_league)
        currency_items = [
            currencyItem
            for currencyItem in currency_items
            if currencyItem.item_id in items_in_current_league_set
        ]
        item_ids = [item.item_id for item in currency_items]

        if not item_ids:
            next_hour = datetime.now().replace(
                minute=0,
                second=0,
                microsecond=0,
            ) + timedelta(hours=1)

            expiration_time = next_hour + timedelta(minutes=random.randint(5, 10))

            self.CurrencyCache[cache_key] = CacheState[CurrencyItemExtended](
                value=[],
                expires=expiration_time,
            )
            return []

        daily_stat_dates = get_daily_stat_dates()
        price_logs = build_daily_stat_price_logs(
            item_ids,
            daily_stat_dates,
            await price_log_repository.get_item_daily_stats(
                item_ids,
                cache_key.league_id,
                cache_key.realm_id,
                daily_stat_dates,
            ),
        )

        reference_currency_price = 1.0
        if cache_key.reference_currency:
            reference_currency_item = await currency_item_repository.get_currency_item(
                cache_key.reference_currency,
                cache_key.game_id,
            )

            if reference_currency_item is None:
                raise Exception()

            reference_currency_price = await price_log_repository.get_item_price(
                reference_currency_item.item_id,
                cache_key.league_id,
                cache_key.realm_id,
                None,
            )
            reference_currency_logs = build_daily_stat_price_logs(
                [reference_currency_item.item_id],
                daily_stat_dates,
                await price_log_repository.get_item_daily_stats(
                    [reference_currency_item.item_id],
                    cache_key.league_id,
                    cache_key.realm_id,
                    daily_stat_dates,
                ),
            )[reference_currency_item.item_id]
            price_logs = convert_price_log_matrix_from_base(
                price_logs,
                reference_currency_logs,
            )

        last_price = dict.fromkeys(item_ids, 0.0)

        prices = await price_log_repository.get_item_prices(
            item_ids, 
            cache_key.league_id,
            cache_key.realm_id)

        prices_lookup = {price.item_id: price for price in prices}
        converted_current_prices = convert_prices_from_base(
            {
                price.item_id: float(price.price)
                for price in prices_lookup.values()
            },
            reference_currency_price,
        )

        items = [
            CurrencyItemExtended(**item.model_dump(), price_logs=price_logs[item.item_id])
            for item in currency_items
        ]

        for item in items:
            last_price[item.item_id] = converted_current_prices[item.item_id]

        items.sort(
            key=lambda item: (
                last_price[item.item_id] if item.item_id in last_price else 0
            ),
            reverse=True,
        )

        items = [
            CurrencyItemExtended(
                **item.model_dump(exclude={"current_price", "current_quantity"}),
                current_price=last_price[item.item_id],
                current_quantity=prices_lookup[item.item_id].quantity,
            )
            for item in items
        ]

        next_hour = datetime.now().replace(
            minute=0,
            second=0,
            microsecond=0,
        ) + timedelta(hours=1)

        expiration_time = next_hour + timedelta(minutes=random.randint(5, 10))

        self.CurrencyCache[cache_key] = CacheState[CurrencyItemExtended](
            value=items,
            expires=expiration_time,
        )

        return items
