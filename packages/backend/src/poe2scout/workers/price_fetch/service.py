import sys
from typing import Dict, List
from pydantic import BaseModel
from poe2scout.integrations.poe.currency_exchange_response import (
    CurrencyExchangeResponse,
    LeagueCurrencyPairData,
)
from poe2scout.db.repositories.currency_exchange_repository import (
    CurrencyExchangeRepository,
)
from poe2scout.db.repositories.item_repository import ItemRepository
from poe2scout.db.repositories.item_repository.record_price import RecordPriceModel
from .functions.fetch_unique import PriceFetchResult, fetch_unique
from .functions.record_price import record_price
import logging
from .config import PriceFetchConfig
from .functions.sync_metadata_and_icon import sync_metadata_and_icon
from datetime import datetime, timezone
from poe2scout.integrations.poe.client import PoeApiClient, PoeTradeClient
from poe2scout.db.repositories.item_repository.get_all_unique_items import UniqueItem
from poe2scout.db.repositories.item_repository.get_all_currency_items import CurrencyItem
from poe2scout.db.repositories.item_repository.get_leagues import League

import asyncio

logger = logging.getLogger(__name__)


async def run(
    config: PriceFetchConfig, 
    repo: ItemRepository, 
    currency_exchange_repo: CurrencyExchangeRepository
):
    # Define the schedule

    logger.info("Price fetch service started.")
    await asyncio.gather(
        run_currency_exchange_prices(repo, config, currency_exchange_repo), fetch_prices(repo)
    )


async def run_currency_exchange_prices(
    repo: ItemRepository, 
    config: PriceFetchConfig, 
    currency_exchange_repo: CurrencyExchangeRepository
):
    headers = {"User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"}
    async with PoeApiClient(
        config.POEAPI_CLIENT_ID, config.POEAPI_CLIENT_SECRET, headers=headers
    ) as client:
        while True:
            await fetch_currency_exchange_prices(repo, config, currency_exchange_repo, client)
            await asyncio.sleep(10)


class CurrencyPrice(BaseModel):
    item_id: str
    value: float  # In exalts
    quantity_traded: int


async def fetch_currency_exchange_prices(
    repo: ItemRepository,
    config: PriceFetchConfig,
    currency_exchange_repo: CurrencyExchangeRepository,
    client: PoeApiClient,
):
    last_fetch_epoch = (
        await currency_exchange_repo.get_service_cache_value("PriceFetch_Currency")
    ).value
    current_epoch = last_fetch_epoch + 60 * 60

    logger.info("Checking for currencies")

    await asyncio.sleep(
        current_epoch + 61 * 60 - int(datetime.now(timezone.utc).timestamp())
    )  # Wait til next time
    leagues = await repo.get_all_leagues()

    url = f"https://www.pathofexile.com/api/currency-exchange/poe2/{current_epoch}"

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
        await currency_exchange_repo.set_service_cache_value("PriceFetch_Currency", current_epoch)
        return
    logger.info("Updating correctly")
    try:
        for league in leagues:
            if await repo.get_prices_checked(current_epoch, league.id):
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
                item_price = await repo.get_item_price(
                    (await repo.get_chaos_item()).item_id, league.id, current_epoch
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
                item_price = await repo.get_item_price(
                    (await repo.get_divine_item()).item_id, league.id, current_epoch
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

            currency_items = await repo.get_currency_items([key for key in final_prices.keys()])

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
                    league_id=league.id,
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
                await repo.record_price_bulk(price_logs, current_epoch)
    except Exception as e:
    # Catches any other unexpected exceptions
        logger.info(f"An unexpected error occurred: {e}")

    logger.info(
                f"Saving cache value. {current_epoch}"
            )
    await currency_exchange_repo.set_service_cache_value("PriceFetch_Currency", current_epoch)
    await currency_exchange_repo.update_pair_histories()


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


async def fetch_prices(repo: ItemRepository):
    headers = {"User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"}
    async with PoeTradeClient(headers=headers) as client:
        while True:
            # Get all unqiue items
            leagues = await repo.get_leagues()
            leagues = [league for league in leagues if league.id == 7] # Fate of the Vaal
            base_unique_items = await repo.get_all_unique_items()
            base_currency_items = await repo.get_all_currency_items()

            exalted_item = await repo.get_exalted_item()
            divine_item = await repo.get_divine_item()

            for league in leagues:
                current_time = datetime.now().strftime("%H")
                fetched_item_ids: list[int] = await repo.get_fetched_item_ids(
                    current_time, league.id
                )
                item_ids = await repo.get_all_items()
                item_ids = [item.id for item in item_ids if item.id not in fetched_item_ids]

                item_ids_to_fetch = [
                    item for item in item_ids if item not in fetched_item_ids
                ]

                unique_items = [
                    item for item in base_unique_items if item.item_id in item_ids_to_fetch
                ]

                logger.info(f"fetching {len(unique_items)} unique items")

                if len(item_ids_to_fetch) == 0:
                    logger.info("No items to fetch")
                    continue

                divine_price = await repo.get_item_price(divine_item.item_id, league.id)

                await process_uniques(
                    unique_items,
                    league,
                    repo,
                    client,
                    exalted_item,
                    divine_item,
                    divine_price,
                )

                currency_items = [item for item in base_currency_items]
                for currency_item in currency_items:
                    if currency_item.item_metadata is None:
                        logger.info(
                            f"Syncing metadata and icon for {currency_item.text}"
                        )
                        await sync_metadata_and_icon(
                            currency_item,
                            repo,
                            client,
                            BASE_URL,
                            REALM,
                            leagues[0].value,
                        )


BASE_URL = "https://www.pathofexile.com/api/trade2"
REALM = "poe2"


async def process_uniques(
    unique_items: list[UniqueItem],
    league: League,
    repo: ItemRepository,
    client: PoeTradeClient,
    exalted_item: CurrencyItem,
    divine_item: CurrencyItem,
    divine_price: float,
):
    for unique_item in unique_items:
        try:
            ### Fetch price of exalt, chaos, div
            ### Use price with highest quantity as the actual price
            ### Gotten rid of all anti price fixing.
            ### After the league has progressed half a day? Turn on instant buy out only.
            logger.info(f"Fetching price for {unique_item.name} in {league.value}")
            exalt_price_fetch_result: PriceFetchResult = await fetch_unique(
                unique_item, league, repo, client, "exalted"
            )
            chaos_price_fetch_result: PriceFetchResult = await fetch_unique(
                unique_item, league, repo, client, "chaos"
            )
            divine_price_fetch_result: PriceFetchResult = await fetch_unique(
                unique_item, league, repo, client, "divine"
            )
            logger.info(f"Exalt price info: {exalt_price_fetch_result}")

            prices: List[PriceFetchResult] = [
                exalt_price_fetch_result,
                chaos_price_fetch_result,
                divine_price_fetch_result,
            ]
            prices = [price for price in prices if price.price > 0]

            if len(prices) == 0:
                logger.info(f"No valid priceFetchResults for {unique_item}")
                continue

            lowest_price = sys.maxsize
            quantity = 0
            for price in prices:
                currency = await repo.get_currency_item(price.currency)
                assert currency is not None

                currency_price = await repo.get_item_price(currency.item_id, league.id)

                item_price = price.price * currency_price
                quantity += price.quantity
                if item_price < lowest_price:
                    lowest_price = item_price

            logger.info(
                f"Recording price for {unique_item.name} in {league.value}" + \
                f"with price {lowest_price} and quantity {quantity}"
            )
            await record_price(
                lowest_price, unique_item.item_id, league.id, quantity, repo
            )
        except:
            logger.error(f"error fetching for {unique_item}")
            raise
