import asyncio
from datetime import datetime, timezone
import logging
from decimal import Decimal
from typing import List

from poe2scout.db.repositories import (
    currency_exchange_repository,
    currency_item_repository,
    league_repository,
    price_log_repository,
    realm_repository,
    service_repository,
)
from poe2scout.db.repositories.currency_item_repository.get_all_currency_items import (
    CurrencyItem,
)
from poe2scout.db.repositories.price_log_repository.get_item_prices_in_range import (
    GetItemPricesInRangeModel,
)
from poe2scout.integrations.poe.client import PoeApiClient
from poe2scout.integrations.poe.currency_exchange_models import (
    CurrencyExchangeSnapshot,
    CurrencyExchangeSnapshotPair,
    CurrencyExchangeSnapshotPairData,
)
from poe2scout.integrations.poe.currency_exchange_response import (
    CurrencyExchangeResponse,
    TradingPair,
)
from poe2scout.workers.currency_exchange.config import CurrencyExchangeServiceConfig

logger = logging.getLogger(__name__)


async def run(
    config: CurrencyExchangeServiceConfig,
    client: PoeApiClient,
):
    current_epoch_utc = int(datetime.now(tz=timezone.utc).timestamp())
    last_fetched_epoch_utc = (
        await service_repository.get_service_cache_value("CurrencyExchange")
    ).value
    last_fetched_price_log_epoch_utc = (
        await service_repository.get_service_cache_value("PriceFetch_Currency")
    ).value

    if last_fetched_price_log_epoch_utc <= last_fetched_epoch_utc:
        logger.info("Up to date with priceFetch")
        await asyncio.sleep(60 * 10)
        return

    realms = await realm_repository.get_realms()
    time_to_fetch_utc = (
        last_fetched_epoch_utc + 60 * 60 if last_fetched_epoch_utc is not None else None
    )

    if time_to_fetch_utc:
        logger.info(f"{time_to_fetch_utc}")
        await asyncio.sleep(time_to_fetch_utc + 60 * 5 - current_epoch_utc)

    next_change_ids = await asyncio.gather(
        *(process_realm_snapshots(client, realm, time_to_fetch_utc) for realm in realms)
    )

    if any(next_change_id is None for next_change_id in next_change_ids):
        return

    data_next_change_id = next_change_ids[0]
    assert data_next_change_id is not None

    await service_repository.set_service_cache_value(
        "CurrencyExchange",
        data_next_change_id - 60 * 60,
    )


async def process_realm_snapshots(
    client: PoeApiClient,
    realm,
    time_to_fetch_utc: int | None,
) -> int | None:
    if time_to_fetch_utc is None:
        if realm.api_id != "pc":
            url = f"https://www.pathofexile.com/api/currency-exchange/{realm.api_id}"
        else:
            url = "https://www.pathofexile.com/api/currency-exchange"
    else:
        if realm.api_id != "pc":
            url = f"https://www.pathofexile.com/api/currency-exchange/{realm.api_id}/{time_to_fetch_utc}"
        else:
            url = f"https://www.pathofexile.com/api/currency-exchange/{time_to_fetch_utc}"

    response = await client.get(url)

    if response.status_code != 200:
        raise Exception("GetFromApiFailure")
    data = CurrencyExchangeResponse.model_validate(response.json())

    fetch_status = await service_repository.get_currency_fetch_status(
        start_time=datetime.fromtimestamp(data.next_change_id)
    )

    if not fetch_status:
        logger.info("Prices not fetched yet")
        await asyncio.sleep(60 * 10)
        return None

    leagues = await league_repository.get_leagues(realm.game_id)

    currencies = await currency_item_repository.get_all_currency_items(realm.game_id)

    currency_lookup_by_api_id = {currency.api_id: currency for currency in currencies}

    league_to_prices_lookup: dict[int, List[GetItemPricesInRangeModel]] = {}

    for league in leagues:
        item_prices = await price_log_repository.get_item_prices_in_range(
            item_ids=[item.item_id for item in currencies],
            league_id=league.league_id,
            realm_id=realm.realm_id,
            start_time=datetime.fromtimestamp(data.next_change_id - 60 * 60),
            end_time=datetime.fromtimestamp(data.next_change_id),
        )
        league_to_prices_lookup[league.league_id] = item_prices

    for league in leagues:
        logger.info(f"analyzing league {league}")

        has_logs = (
            True
            if len(
                [
                    item_price
                    for item_price in league_to_prices_lookup[league.league_id]
                    if item_price.price != 0
                ]
            )
            > 0
            else False
        )

        if not has_logs:
            logger.info(
                f"Skipping league {league} cause no prices recorded at this time"
            )
            continue
        item_price_lookup_by_item_id = {
            item.item_id: item for item in league_to_prices_lookup[league.league_id]
        }

        pairs = [pair for pair in data.markets if pair.league == league.value]

        snapshot = CurrencyExchangeSnapshot(
            epoch=data.next_change_id - 60 * 60,
            league_id=league.league_id,
            realm_id=realm.realm_id,
            pairs=[]
        )

        present_api_ids = currency_lookup_by_api_id.keys()
        for pair in pairs:
            pair_currencies = pair.market_id.split("|")
            if (
                pair_currencies[0] not in present_api_ids
                or pair_currencies[1] not in present_api_ids
            ):
                logger.error(
                    "One of the currencies in "
                    f"{pair_currencies} is not present in db. Skipping pair"
                )
                continue

            currency_one = currency_lookup_by_api_id[pair_currencies[0]]
            currency_two = currency_lookup_by_api_id[pair_currencies[1]]

            currency_one_data = get_pair_data(
                currency_one, item_price_lookup_by_item_id, pair, currency_two
            )
            currency_two_data = get_pair_data(
                currency_two, item_price_lookup_by_item_id, pair, currency_one
            )

            most_liquid_currency = (
                currency_one_data
                if item_price_lookup_by_item_id[currency_one.item_id].quantity
                > item_price_lookup_by_item_id[currency_two.item_id].quantity
                else currency_two_data
            )

            snapshot_pair = CurrencyExchangeSnapshotPair(
                currency_one_item_id=currency_one.item_id,
                currency_two_item_id=currency_two.item_id,
                volume=most_liquid_currency.value_traded,
                currency_one_data=currency_one_data,
                currency_two_data=currency_two_data,
            )

            snapshot.pairs.append(snapshot_pair)

        volume = 0
        market_cap = 0
        for pair in snapshot.pairs:
            volume += pair.volume
            market_cap += pair.currency_one_data.stock_value
            market_cap += pair.currency_two_data.stock_value

        snapshot.volume = Decimal(volume)
        snapshot.market_cap = Decimal(market_cap)

        logger.info(f"Saving {len(snapshot.pairs)} for {snapshot.league_id}")
        if volume == 0 and market_cap == 0:
            logger.info("No data in snapshot. Skipping")
            continue
        await currency_exchange_repository.create_snapshot(snapshot)

    return data.next_change_id


def get_pair_data(
    currency_item: CurrencyItem,
    item_price_lookup: dict[int, GetItemPricesInRangeModel],
    pair: TradingPair,
    other_currency_item: CurrencyItem,
) -> CurrencyExchangeSnapshotPairData:
    volume_traded = pair.volume_traded[currency_item.api_id]
    value_traded = volume_traded * item_price_lookup[currency_item.item_id].price
    if volume_traded != 0:
        relative_price = (
            Decimal(pair.volume_traded[other_currency_item.api_id] / volume_traded)
            * item_price_lookup[other_currency_item.item_id].price
        )
    else:
        relative_price = Decimal(0)
    highest_stock = pair.highest_stock[currency_item.api_id]

    return CurrencyExchangeSnapshotPairData(
        volume_traded=volume_traded,
        value_traded=value_traded,
        relative_price=relative_price,
        highest_stock=highest_stock,
        stock_value=highest_stock * item_price_lookup[currency_item.item_id].price,
    )
