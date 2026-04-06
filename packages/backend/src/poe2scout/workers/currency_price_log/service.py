from typing import Dict, List
from poe2scout.db.repositories import (
    currency_exchange_repository, 
    currency_item_repository, 
    league_repository, 
    price_log_repository,
    realm_repository, 
    service_repository, 
)
from pydantic import BaseModel
from poe2scout.integrations.poe.currency_exchange_response import (
    CurrencyExchangeResponse,
    LeagueCurrencyPairData,
)
from poe2scout.db.repositories.price_log_repository.record_price import RecordPriceModel
import logging
from .config import PriceFetchConfig
from datetime import datetime, timezone
from poe2scout.integrations.poe.client import PoeApiClient
from poe2scout.db.repositories.league_repository.get_leagues import League

import asyncio

logger = logging.getLogger(__name__)
    

async def run_currency_exchange_prices(config: PriceFetchConfig):
    headers = {"User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"}
    async with PoeApiClient(
        config.POEAPI_CLIENT_ID, config.POEAPI_CLIENT_SECRET, headers=headers
    ) as client:
        while True:
            await fetch_currency_exchange_prices(
                config, 
                client
            )


class CurrencyPrice(BaseModel):
    item_id: str
    value: float  # In exalts
    quantity_traded: int


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
    )  # Wait til next time
    realms = await realm_repository.get_realms()

    await asyncio.gather(
        *(process_realm_prices(client, current_epoch, realm) for realm in realms)
    )

    logger.info(
                f"Saving cache value. {current_epoch}"
            )
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

        base_currencies: List[str] = ["divine", "chaos", "exalted"]

        exalted_price = CurrencyPrice(item_id="exalted", value=1.0, quantity_traded=1)

        data = CurrencyExchangeResponse.model_validate(response.json())

        if data.next_change_id == current_epoch:
            logger.error("Reached the end. Somethings gone wrong.")
            await asyncio.sleep(60 * 10)

            return

        if len(data.markets) == 0:  # Current timestamp. Not filled in yet
            logger.info("No pairs in markets.")
            return
        logger.info("Updating correctly")

        leagues = await league_repository.get_leagues(realm.game_id)

        try:
            for league in leagues:
                if await price_log_repository.get_prices_checked(current_epoch, league.league_id, realm.realm_id):
                    logger.info(
                        "Price already checked for this timestamp and league. continuing"
                    )
                    continue

                ### Calculate baseCurrency prices (Divine, Chaos, Exalted)
                pairs = await get_league_data(data, league, base_currencies)
                chaos_pairs = [
                    pair
                    for pair in pairs
                    if pair.target_item == "chaos" and pair.base_item == "exalted"
                ]  # only exalted - chaos

                chaos_price = None
                if len(chaos_pairs) == 0:
                    logger.info("No chaos pair")
                    item_price = await price_log_repository.get_item_price(
                        (await currency_item_repository.get_chaos_item(realm.game_id)).item_id, 
                        league.league_id, 
                        realm.realm_id,
                        current_epoch
                    )
                    if item_price == 0:
                        continue

                    chaos_price = CurrencyPrice(
                        item_id="chaos", value=item_price, quantity_traded=0
                    )
                else:
                    for chaos_pair in chaos_pairs:
                        pairs.remove(chaos_pair)
                        chaos_price = CurrencyPrice(
                            item_id="chaos",
                            value=chaos_pair.value_of_target_item_in_base_items,
                            quantity_traded=chaos_pair.quantity_of_target_item,
                        )

                assert chaos_price is not None

                divine_pairs = [
                    pair for pair in pairs if pair.target_item == "divine"
                ]  # only exalted - divine and chaos - divine
                divine_prices: List[float] = []
                divine_trading_quantities = []
                for divine_pair in divine_pairs:
                    pairs.remove(divine_pair)
                    if divine_pair.base_item == "exalted":
                        divine_prices.append(divine_pair.value_of_target_item_in_base_items)
                        divine_trading_quantities.append(divine_pair.quantity_of_target_item)
                    else:
                        if divine_pair.base_item != "chaos":
                            raise Exception(
                                "Somehow got trading pair for divine that wasnt exalted or chaos"
                            )
                        divine_prices.append(
                            divine_pair.value_of_target_item_in_base_items * chaos_price.value
                        )
                        divine_trading_quantities.append(divine_pair.quantity_of_target_item)

                if len(divine_prices) == 0:
                    logger.info("No divine pair")
                    item_price = await price_log_repository.get_item_price(
                        (await currency_item_repository.get_divine_item(realm.game_id)).item_id, 
                        league.league_id, 
                        realm.realm_id,
                        current_epoch
                    )
                    if item_price == 0:
                        continue

                    divine_prices.append(item_price)

                divine_price = CurrencyPrice(
                    item_id="divine",
                    value=sum(divine_prices) / len(divine_prices),
                    quantity_traded=sum(divine_trading_quantities),
                )

                base_item_prices = [exalted_price, chaos_price, divine_price]

                target_item_prices: List[CurrencyPrice] = []
                for pair in pairs:
                    target_item_prices.append(get_currency_price_from_pair(pair, base_item_prices))

                item_price_mapping: Dict[str, List[CurrencyPrice]] = {}
                item_price_mapping[divine_price.item_id] = [divine_price]
                item_price_mapping[exalted_price.item_id] = [exalted_price]
                item_price_mapping[chaos_price.item_id] = [chaos_price]

                for target_item_price in target_item_prices:
                    if target_item_price.item_id not in item_price_mapping.keys():
                        item_price_mapping[target_item_price.item_id] = [target_item_price]
                    else:
                        item_price_mapping[target_item_price.item_id].append(target_item_price)

                final_prices: Dict[str, CurrencyPrice] = {}
                for key in item_price_mapping.keys():
                    currency_prices = item_price_mapping[key]

                    weighted_price = 0

                    tuples = [(cp.value, cp.quantity_traded) for cp in currency_prices]
                    total_quantity = sum([item[1] for item in tuples])

                    for value, quantity in tuples:
                        if total_quantity == 0:
                            continue
                        weighted_price += value * (quantity / total_quantity)
                    final_prices[key] = CurrencyPrice(
                        item_id=key, value=weighted_price, quantity_traded=total_quantity
                    )

                ### Record pricelogs

                currency_items = await currency_item_repository.get_currency_items(
                    [key for key in final_prices.keys()],
                    realm.game_id
                )

                item_id_lookup: Dict[str, int] = {}

                for currency_item in currency_items:
                    item_id_lookup[currency_item.api_id] = currency_item.item_id

                valid_currency_item_api_ids = set(item_id_lookup.keys())
                for key in list(final_prices.keys()):
                    if key not in valid_currency_item_api_ids:
                        final_prices.pop(key)

                price_logs = [
                    RecordPriceModel(
                        item_id=item_id_lookup[value.item_id],
                        league_id=league.league_id,
                        realm_id=realm.realm_id,
                        price=value.value,
                        quantity=value.quantity_traded,
                    )
                    for value in final_prices.values()
                    if value.value != 0
                ]

                if len(price_logs) == 1 and price_logs[0].item_id == exalted_price.item_id:
                    logger.info("Only price is exalted. Skipping save.")
                else:
                    logger.info(
                        f"Saving {len(price_logs)} logs for {league.value} at {current_epoch} "
                        + f"or more specifically {datetime.fromtimestamp(current_epoch)}"
                    )
                    await price_log_repository.record_price_bulk(price_logs, current_epoch)
        except Exception as e:
        # Catches any other unexpected exceptions
            logger.info(f"An unexpected error occurred: {e}")


def get_currency_price_from_pair(
    pair: LeagueCurrencyPairData, base_item_prices: List[CurrencyPrice]
) -> CurrencyPrice:
    for base_item_price in base_item_prices:
        if pair.base_item != base_item_price.item_id:
            continue

        return CurrencyPrice(
            item_id=pair.target_item,
            value=pair.value_of_target_item_in_base_items * base_item_price.value,
            quantity_traded=pair.quantity_of_target_item,
        )
    else:
        raise Exception("Somehow didnt find baseItemPrice for a pairs baseItem")


async def get_league_data(
    data: CurrencyExchangeResponse, league: League, base_items: List[str]
) -> List[LeagueCurrencyPairData]:
    pairs: List[LeagueCurrencyPairData] = []
    current_league_markets = [
        pair for pair in data.markets if pair.league == league.value
    ]
    for listing in current_league_markets:
        item1, item2 = listing.market_id.split("|")

        # No important baseCurrency in pair.
        if not (item1 in base_items or item2 in base_items):
            continue

        if listing.volume_traded[item1] == 0:
            continue

        # Pair is 2 important baseCurrencies
        # Create a pair for each side
        # else
        # just create a pair with exalted as the base
        if item1 in base_items and item2 in base_items:
            if item1 != "exalted" and item2 != "exalted":
                if item1 == "chaos":
                    base_item = item1
                    target_item = item2
                else:
                    base_item = item2
                    target_item = item1
            elif item1 == "exalted":
                base_item = item1
                target_item = item2
            else:
                base_item = item2
                target_item = item1
        elif item1 in base_items:
            base_item = item1
            target_item = item2
        else:
            base_item = item2
            target_item = item1

        value_of_target = (
            listing.volume_traded[base_item] / listing.volume_traded[target_item]
        )  # 1 / 300 # 0.0033 value of target item in divines.
        quantity_of_pair_traded = listing.volume_traded[
            target_item
        ]  # 300. How many people actually traded in this item for that.
        pairs.append(
            LeagueCurrencyPairData(
                league=league,
                base_item=base_item,
                target_item=target_item,
                value_of_target_item_in_base_items=value_of_target,
                quantity_of_target_item=quantity_of_pair_traded,
            )
        )

    return pairs


BASE_URL = "https://www.pathofexile.com/api/trade2"
REALM = "poe2"
