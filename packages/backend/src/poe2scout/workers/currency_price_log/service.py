import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel

from poe2scout.db.repositories import (
    currency_exchange_repository,
    currency_item_repository,
    league_repository,
    price_log_repository,
    realm_repository,
    service_repository,
)
from poe2scout.db.repositories.league_repository.get_leagues import League
from poe2scout.db.repositories.price_log_repository.record_price import RecordPriceModel
from poe2scout.integrations.poe.client import PoeApiClient
from poe2scout.integrations.poe.currency_exchange_response import (
    CurrencyExchangeResponse,
    TradingPair,
)

from .config import PriceFetchConfig

logger = logging.getLogger(__name__)


class CurrencyPrice(BaseModel):
    item_id: str
    value: float  # In the league base currency.
    quantity_traded: int


class PriceObservation(BaseModel):
    base_item: str
    target_item: str
    value_of_target_item_in_base_items: float
    quantity_of_target_item: int


async def run_currency_exchange_prices(config: PriceFetchConfig):
    headers = {"User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"}
    async with PoeApiClient(
        config.POEAPI_CLIENT_ID, config.POEAPI_CLIENT_SECRET, headers=headers
    ) as client:
        while True:
            await fetch_currency_exchange_prices(config, client)


async def fetch_currency_exchange_prices(
    config: PriceFetchConfig,
    client: PoeApiClient,
):
    last_fetch_epoch = (
        await service_repository.get_service_cache_value("PriceFetch_Currency")
    ).value
    current_epoch = last_fetch_epoch + 60 * 60

    logger.info("Checking for currencies")

    await asyncio.sleep(
        current_epoch + 61 * 60 - int(datetime.now(timezone.utc).timestamp())
    )
    realms = await realm_repository.get_realms()

    await asyncio.gather(
        *(process_realm_prices(client, current_epoch, realm) for realm in realms)
    )

    logger.info(f"Saving cache value. {current_epoch}")
    await service_repository.set_service_cache_value("PriceFetch_Currency", current_epoch)
    await currency_exchange_repository.update_pair_histories()


async def process_realm_prices(
    client: PoeApiClient,
    current_epoch: int,
    realm,
):
    if realm.api_id != "pc":
        url = f"https://www.pathofexile.com/api/currency-exchange/{realm.api_id}/{current_epoch}"
    else:
        url = f"https://www.pathofexile.com/api/currency-exchange/{current_epoch}"

    response = await client.get(url)
    if response.status_code != 200:
        logger.error(response.json())
        raise Exception("GetFromApiFailure")

    data = CurrencyExchangeResponse.model_validate(response.json())

    if data.next_change_id == current_epoch:
        logger.error("Reached the end. Somethings gone wrong.")
        await asyncio.sleep(60 * 10)
        return

    if len(data.markets) == 0:
        logger.info("No pairs in markets.")
        return

    logger.info("Updating correctly")

    leagues = await league_repository.get_leagues(realm.game_id)
    currency_items = await currency_item_repository.get_all_currency_items(realm.game_id)
    item_id_lookup = {
        currency_item.api_id: currency_item.item_id for currency_item in currency_items
    }

    try:
        for league in leagues:
            if await price_log_repository.get_prices_checked(
                current_epoch,
                league.league_id,
                realm.realm_id,
            ):
                logger.info(
                    "Price already checked for this timestamp and league. continuing"
                )
                continue

            final_prices = await build_final_prices_for_league(
                data=data,
                league=league,
            )

            price_logs = [
                RecordPriceModel(
                    item_id=item_id_lookup[value.item_id],
                    league_id=league.league_id,
                    realm_id=realm.realm_id,
                    price=value.value,
                    quantity=value.quantity_traded,
                )
                for value in final_prices.values()
                if value.item_id in item_id_lookup and value.value != 0
            ]

            if (
                len(price_logs) == 1
                and price_logs[0].item_id == league.base_currency_item_id
            ):
                logger.info("Only price is the league base currency. Skipping save.")
                continue

            logger.info(
                f"Saving {len(price_logs)} logs for {league.value} at {current_epoch} "
                + f"or more specifically {datetime.fromtimestamp(current_epoch)}"
            )
            await price_log_repository.record_price_bulk(price_logs, current_epoch)
    except Exception as exc:
        logger.info(f"An unexpected error occurred: {exc}")
        raise


async def build_final_prices_for_league(
    data: CurrencyExchangeResponse,
    league: League,
) -> Dict[str, CurrencyPrice]:
    observations = get_league_observations(data, league)
    resolved_prices: Dict[str, CurrencyPrice] = {
        league.base_currency_api_id: CurrencyPrice(
            item_id=league.base_currency_api_id,
            value=1.0,
            quantity_traded=1,
        )
    }
    price_depths: dict[str, int] = {league.base_currency_api_id: 0}

    direct_prices = aggregate_prices_from_observations(
        [
            observation
            for observation in observations
            if observation.base_item == league.base_currency_api_id
        ],
        resolved_prices,
        price_depths,
    )
    resolved_prices.update(direct_prices)
    for currency_api_id in direct_prices:
        price_depths[currency_api_id] = 1

    while True:
        next_prices = aggregate_prices_from_observations(
            observations,
            resolved_prices,
            price_depths,
        )
        pending_prices = {
            currency_api_id: price
            for currency_api_id, price in next_prices.items()
            if currency_api_id not in resolved_prices
        }
        if not pending_prices:
            break

        resolved_prices.update(pending_prices)
        for currency_api_id, _price in pending_prices.items():
            matching_depth = min(
                price_depths[observation.base_item] + 1
                for observation in observations
                if observation.target_item == currency_api_id
                and observation.base_item in price_depths
            )
            price_depths[currency_api_id] = matching_depth

    return resolved_prices


def aggregate_prices_from_observations(
    observations: list[PriceObservation],
    resolved_prices: dict[str, CurrencyPrice],
    price_depths: dict[str, int],
) -> Dict[str, CurrencyPrice]:
    price_candidates: Dict[str, list[tuple[int, float, int]]] = {}

    for observation in observations:
        base_price = resolved_prices.get(observation.base_item)
        base_depth = price_depths.get(observation.base_item)
        if base_price is None or base_depth is None:
            continue

        price_candidates.setdefault(observation.target_item, []).append(
            (
                base_depth + 1,
                observation.value_of_target_item_in_base_items * base_price.value,
                observation.quantity_of_target_item,
            )
        )

    aggregated_prices: Dict[str, CurrencyPrice] = {}
    for currency_api_id, candidates in price_candidates.items():
        min_depth = min(candidate[0] for candidate in candidates)
        best_candidates = [
            candidate for candidate in candidates if candidate[0] == min_depth
        ]
        total_quantity = sum(candidate[2] for candidate in best_candidates)

        if total_quantity == 0:
            continue

        weighted_price = sum(
            price * (quantity / total_quantity)
            for _, price, quantity in best_candidates
        )
        aggregated_prices[currency_api_id] = CurrencyPrice(
            item_id=currency_api_id,
            value=weighted_price,
            quantity_traded=total_quantity,
        )

    return aggregated_prices


def get_league_observations(
    data: CurrencyExchangeResponse,
    league: League,
) -> List[PriceObservation]:
    observations: List[PriceObservation] = []
    current_league_markets = [
        pair for pair in data.markets if pair.league == league.value
    ]

    for listing in current_league_markets:
        item_one, item_two = listing.market_id.split("|")

        observations.extend(
            create_pair_observations(
                listing=listing,
                item_one=item_one,
                item_two=item_two,
            )
        )

    return observations


def create_pair_observations(
    listing: TradingPair,
    item_one: str,
    item_two: str,
) -> list[PriceObservation]:
    item_one_volume = listing.volume_traded[item_one]
    item_two_volume = listing.volume_traded[item_two]

    if item_one_volume == 0 or item_two_volume == 0:
        return []

    return [
        PriceObservation(
            base_item=item_one,
            target_item=item_two,
            value_of_target_item_in_base_items=item_one_volume / item_two_volume,
            quantity_of_target_item=item_two_volume,
        ),
        PriceObservation(
            base_item=item_two,
            target_item=item_one,
            value_of_target_item_in_base_items=item_two_volume / item_one_volume,
            quantity_of_target_item=item_one_volume,
        ),
    ]


BASE_URL = "https://www.pathofexile.com/api/trade2"
REALM = "poe2"
