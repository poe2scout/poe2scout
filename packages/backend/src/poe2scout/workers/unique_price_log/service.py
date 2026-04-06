import sys
from typing import List
from poe2scout.db.repositories import (
    currency_item_repository,
    item_repository, 
    league_repository, 
    price_log_repository, 
    service_repository, 
    unique_item_repository
)
from .functions.fetch_unique import PriceFetchResult, fetch_unique
from .functions.record_price import record_price
from .functions.sync_metadata_and_icon import sync_metadata_and_icon
import logging
from datetime import datetime
from poe2scout.integrations.poe.client import PoeTradeClient
from poe2scout.db.repositories.unique_item_repository.get_all_unique_items import UniqueItem
from poe2scout.db.repositories.league_repository.get_leagues import League


logger = logging.getLogger(__name__)

BASE_URL = "https://www.pathofexile.com/api/trade2"
REALM = "poe2"

async def fetch_prices():
    headers = {"User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"}
    async with PoeTradeClient(headers=headers) as client:
        while True:
            # Get all unqiue items
            game_id = 2
            league = await league_repository.get_league(7)
            realm_id = 4
            base_unique_items = await unique_item_repository.get_all_unique_items(game_id)
            base_currency_items = await currency_item_repository.get_all_currency_items(game_id)

            current_time = datetime.now().strftime("%H")
            fetched_item_ids: list[int] = await service_repository.get_fetched_item_ids(
                current_time, league.league_id
            )
            item_ids = await item_repository.get_all_items(game_id)
            item_ids = [
                item.item_id for item in item_ids if item.item_id not in fetched_item_ids
            ]

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

            await process_uniques(
                unique_items,
                league,
                client,
                game_id,
                realm_id
            )

            currency_items = [item for item in base_currency_items]
            for currency_item in currency_items:
                if currency_item.item_metadata is None:
                    logger.info(
                        f"Syncing metadata and icon for {currency_item.text}"
                    )
                    await sync_metadata_and_icon(
                        currency_item,
                        client,
                        BASE_URL,
                        REALM,
                        league.value,
                    )


async def process_uniques(
    unique_items: list[UniqueItem],
    league: League,
    client: PoeTradeClient,
    game_id: int,
    realm_id: int
):
    for unique_item in unique_items:
        try:
            ### Fetch price of exalt, chaos, div
            ### Use price with highest quantity as the actual price
            ### Gotten rid of all anti price fixing.
            ### After the league has progressed half a day? Turn on instant buy out only.
            logger.info(f"Fetching price for {unique_item.name} in {league.value}")
            exalt_price_fetch_result: PriceFetchResult = await fetch_unique(
                unique_item, league, client, "exalted"
            )
            chaos_price_fetch_result: PriceFetchResult = await fetch_unique(
                unique_item, league, client, "chaos"
            )
            divine_price_fetch_result: PriceFetchResult = await fetch_unique(
                unique_item, league, client, "divine"
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
                currency = await currency_item_repository.get_currency_item(price.currency, game_id)
                assert currency is not None

                currency_price = await price_log_repository.get_item_price(
                    currency.item_id, 
                    league.league_id,
                    realm_id,
                    None
                )

                item_price = price.price * currency_price
                quantity += price.quantity
                if item_price < lowest_price:
                    lowest_price = item_price

            logger.info(
                f"Recording price for {unique_item.name} in {league.value}" + \
                f"with price {lowest_price} and quantity {quantity}"
            )
            await record_price(
                lowest_price, 
                unique_item.item_id, 
                league.league_id, 
                realm_id,
                quantity
            )
        except:
            logger.error(f"error fetching for {unique_item}")
            raise
