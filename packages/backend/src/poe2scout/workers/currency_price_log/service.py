import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Mapping

from pydantic import BaseModel

from poe2scout.db.repositories import (
    currency_exchange_repository,
    currency_item_repository,
    game_repository,
    league_repository,
    price_log_repository,
    realm_repository,
    service_repository,
)
from poe2scout.db.repositories.game_repository import BridgeCurrency
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


class PriceCandidate(BaseModel):
    value: float
    quantity: int


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

    await asyncio.sleep(current_epoch + 61 * 60 - int(datetime.now(timezone.utc).timestamp()))
    realms = await realm_repository.get_realms()

    await asyncio.gather(*(process_realm_prices(client, current_epoch, realm) for realm in realms))

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
    bridge_currencies = await game_repository.get_bridge_currencies(realm.game_id)
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
                logger.info("Price already checked for this timestamp and league. continuing")
                continue

            final_prices = await build_final_prices_for_league(
                data=data,
                league=league,
                bridge_currencies=bridge_currencies,
                realm_id=realm.realm_id,
                epoch=current_epoch,
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

            if len(price_logs) == 0:
                logger.info(f"no prices found for {league.value}")
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
    bridge_currencies: list[BridgeCurrency],
    realm_id: int,
    epoch: int,
) -> Dict[str, CurrencyPrice]:
    observations = get_league_observations(data, league)

    if len(observations) == 0:
        return {}

    historical_bridge_prices = {}
    if bridge_currencies:
        bridge_prices = await price_log_repository.get_item_prices_before(
            [item.item_id for item in bridge_currencies],
            league.league_id,
            realm_id,
            epoch,
        )
        historical_bridge_prices = {
            bridge_item.api_id: price.price
            for bridge_item, price in zip(bridge_currencies, bridge_prices, strict=False)
            if price.price != 0
        }

    return build_final_prices_from_observations(
        observations=observations,
        league=league,
        bridge_currencies=bridge_currencies,
        fallback_bridge_prices=historical_bridge_prices,
    )


def build_final_prices_from_observations(
    observations: list[PriceObservation],
    league: League,
    bridge_currencies: list[BridgeCurrency],
    fallback_bridge_prices: Mapping[str, float],
) -> Dict[str, CurrencyPrice]:
    # Keep this aggregation linear-ish in the market snapshot size: this worker runs
    # against hourly full-market snapshots and is guarded by a load/performance test.
    observations_by_target: dict[str, list[PriceObservation]] = defaultdict(list)
    for observation in observations:
        observations_by_target[observation.target_item].append(observation)

    resolved_prices: Dict[str, CurrencyPrice] = {
        league.base_currency_api_id: CurrencyPrice(
            item_id=league.base_currency_api_id,
            value=1.0,
            quantity_traded=max(
                get_total_quantity(observations_by_target, league.base_currency_api_id),
                1,
            ),
        )
    }
    resolved_quote_items = {league.base_currency_api_id}

    for bridge_item in bridge_currencies:
        target_observations = observations_by_target.get(bridge_item.api_id, [])
        direct_base_pairs = [
            observation
            for observation in target_observations
            if observation.base_item == league.base_currency_api_id
        ]
        bridge_price = (
            aggregate_target_price(
                target_observations,
                resolved_prices,
                allowed_bases=resolved_quote_items,
            )
            if direct_base_pairs
            else None
        )

        if bridge_price is None:
            fallback_price = fallback_bridge_prices.get(bridge_item.api_id)
            if fallback_price is None:
                continue

            bridge_price = fallback_price

        resolved_prices[bridge_item.api_id] = CurrencyPrice(
            item_id=bridge_item.api_id,
            value=bridge_price,
            quantity_traded=get_total_quantity(observations_by_target, bridge_item.api_id),
        )
        resolved_quote_items.add(bridge_item.api_id)

    bridge_api_ids = {bridge_item.api_id for bridge_item in bridge_currencies}
    for item_api_id in sorted(observations_by_target):
        if item_api_id == league.base_currency_api_id or item_api_id in bridge_api_ids:
            continue

        item_price = aggregate_target_price(
            observations_by_target[item_api_id],
            resolved_prices,
            allowed_bases=resolved_quote_items,
        )
        if item_price is None:
            continue

        resolved_prices[item_api_id] = CurrencyPrice(
            item_id=item_api_id,
            value=item_price,
            quantity_traded=get_total_quantity(observations_by_target, item_api_id),
        )

    return resolved_prices


def get_total_quantity(
    observations_by_target: Mapping[str, list[PriceObservation]],
    target_item: str,
) -> int:
    return sum(
        observation.quantity_of_target_item
        for observation in observations_by_target.get(target_item, [])
    )


def aggregate_target_price(
    observations: list[PriceObservation],
    resolved_prices: Mapping[str, CurrencyPrice],
    allowed_bases: set[str],
) -> float | None:
    candidates: list[PriceCandidate] = []
    for observation in observations:
        if observation.base_item not in allowed_bases:
            continue

        base_price = resolved_prices.get(observation.base_item)
        if base_price is None:
            continue

        candidates.append(
            PriceCandidate(
                value=observation.value_of_target_item_in_base_items * base_price.value,
                quantity=observation.quantity_of_target_item,
            )
        )

    return aggregate_weighted_price(candidates)


def aggregate_weighted_price(candidates: list[PriceCandidate]) -> float | None:
    total_quantity = sum(candidate.quantity for candidate in candidates)
    if total_quantity == 0:
        return None

    return sum(candidate.value * candidate.quantity for candidate in candidates) / total_quantity


def get_league_observations(
    data: CurrencyExchangeResponse,
    league: League,
) -> List[PriceObservation]:
    observations: List[PriceObservation] = []
    current_league_markets = [pair for pair in data.markets if pair.league == league.value]

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
