import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
import logging
import random
from typing import Generic, List, TypeVar

from pydantic import BaseModel
from poe2scout.db.repositories.item_repository import ItemRepository
from poe2scout.db.repositories.models import (
    CurrencyItemExtended,
    PriceLogEntry,
    UniqueItemExtended,
)

T = TypeVar("T")

logger = logging.getLogger(__name__)


class CacheState(BaseModel, Generic[T]):
    value: List[T]
    expires: datetime


class CacheKey(BaseModel):
    category: str
    league_id: int
    reference_currency: str

    class Config:
        frozen = True


class EconomyCache:
    CurrencyCache: dict[CacheKey, CacheState[CurrencyItemExtended]]
    UniqueCache: dict[CacheKey, CacheState[UniqueItemExtended]]

    CurrencyLocks: dict[CacheKey, asyncio.Lock]

    repo: ItemRepository

    def __init__(self, repo: ItemRepository):
        self.CurrencyCache = {}
        self.UniqueCache = {}
        self.repo = repo
        self.CurrencyLocks = defaultdict(asyncio.Lock)

    async def get_currency_page(
        self, 
        league_id: int, 
        category: str, 
        reference_currency: str,
        search: str, 
    ) -> List[CurrencyItemExtended]:
        items: List[CurrencyItemExtended]
        cache_key = CacheKey(
            category=category, league_id=league_id, reference_currency=reference_currency
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
        category: str, 
        search: str, 
        reference_currency: str
    ) -> List[UniqueItemExtended]:
        items: List[UniqueItemExtended]

        cache_key = CacheKey(
            category=category, league_id=league_id, reference_currency=reference_currency
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
        if search != "":
            items = [item for item in items if item.name.lower() == search.lower()]

        return items

    async def fetch_unique_page(self, cache_key: CacheKey) -> List[UniqueItemExtended]:
        unique_items = await self.repo.get_unique_items_by_category(cache_key.category)

        items_in_current_league = await self.repo.get_items_in_current_league(
            cache_key.league_id
        )

        unique_items = [
            uniqueItem
            for uniqueItem in unique_items
            if uniqueItem.item_id in items_in_current_league
        ]
        item_ids = [item.item_id for item in unique_items]

        price_logs = await self.repo.get_item_price_logs(item_ids, cache_key.league_id)

        chaos_price = 1
        if cache_key.reference_currency == "chaos":
            chaos_item = await self.repo.get_currency_item("chaos")
            if chaos_item is None:
                raise Exception()

            chaos_price = await self.repo.get_item_price(
                chaos_item.item_id, cache_key.league_id
            )
            chaos_price_logs = (
                await self.repo.get_item_price_logs([chaos_item.item_id], cache_key.league_id)
            )[chaos_item.item_id]

            for item_price_logs in price_logs:
                for i, item_price_log_list_item in enumerate(price_logs[item_price_logs]):
                    chaos_price_item = chaos_price_logs[i]
                    if item_price_log_list_item is None or chaos_price_item is None:
                        continue

                    price_logs[item_price_logs][i] = PriceLogEntry(
                        price=item_price_log_list_item.price / chaos_price_item.price,
                        time=item_price_log_list_item.time,
                        quantity=item_price_log_list_item.quantity,
                    )

        items = [
            UniqueItemExtended(**item.model_dump(), price_logs=price_logs[item.item_id])
            for item in unique_items
        ]

        last_price = dict.fromkeys(item_ids, 0.0)

        prices = await self.repo.get_item_prices(item_ids, cache_key.league_id)

        prices_lookup = {price.item_id: price for price in prices}

        for item in items:
            last_price[item.item_id] = prices_lookup[item.item_id].price / chaos_price

        items.sort(
            key=lambda item: (
                last_price[item.item_id] if item.item_id in last_price else 0
            ),
            reverse=True,
        )

        items = [
            UniqueItemExtended(
                **item.model_dump(exclude={"currentPrice"}),
                current_price=last_price[item.item_id],
            )
            for item in items
        ]

        self.UniqueCache[cache_key] = CacheState[UniqueItemExtended](
            value=items,
            expires=datetime.now() + timedelta(hours=1, minutes=random.randint(0, 15)),
        )

        return items

    async def fetch_currency_page(self, cache_key: CacheKey) -> List[CurrencyItemExtended]:
        items_in_current_league = await self.repo.get_items_in_current_league(
            cache_key.league_id
        )
        currency_items = await self.repo.get_currency_items_by_category(cache_key.category)
        currency_items = [
            currencyItem
            for currencyItem in currency_items
            if currencyItem.item_id in items_in_current_league
        ]
        item_ids = [item.item_id for item in currency_items]

        price_logs = await self.repo.get_item_price_logs(item_ids, cache_key.league_id)

        chaos_price = 1
        if cache_key.reference_currency == "chaos":
            chaos_item = await self.repo.get_currency_item("chaos")

            if chaos_item is None:
                raise Exception()

            chaos_price = await self.repo.get_item_price(
                chaos_item.item_id, cache_key.league_id
            )
            chaos_price_loags = (
                await self.repo.get_item_price_logs([chaos_item.item_id], cache_key.league_id)
            )[chaos_item.item_id]

            for item_price_logs in price_logs:
                for i, item_price_log_list_item in enumerate(price_logs[item_price_logs]):
                    chaos_price_item = chaos_price_loags[i]
                    if item_price_log_list_item is None or chaos_price_item is None:
                        continue

                    price_logs[item_price_logs][i] = PriceLogEntry(
                        price=item_price_log_list_item.price / chaos_price_item.price,
                        time=item_price_log_list_item.time,
                        quantity=item_price_log_list_item.quantity,
                    )

        items = [
            CurrencyItemExtended(**item.model_dump(), price_logs=price_logs[item.item_id])
            for item in currency_items
        ]

        last_price = dict.fromkeys(item_ids, 0.0)

        prices = await self.repo.get_item_prices(item_ids, cache_key.league_id)

        prices_lookup = {price.item_id: price for price in prices}

        for item in items:
            last_price[item.item_id] = prices_lookup[item.item_id].price / chaos_price

        items.sort(
            key=lambda item: (
                last_price[item.item_id] if item.item_id in last_price else 0
            ),
            reverse=True,
        )

        items = [
            CurrencyItemExtended(
                **item.model_dump(exclude={"currentPrice"}),
                current_price=last_price[item.item_id],
            )
            for item in items
        ]

        next_hour = (datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))

        expiration_time = next_hour + timedelta(minutes=random.randint(5, 10))

        self.CurrencyCache[cache_key] = CacheState[CurrencyItemExtended](
            value=items,
            expires=expiration_time,
        )

        return items
