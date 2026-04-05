from poe2scout.db.repositories.base_repository import BaseRepository
import logging
from httpx import Client
from asyncio import sleep

from poe2scout.shared import constants
from poe2scout.workers.item_sync.models import CurrencyResponse, ItemResponse
from .functions.sync_currencies import sync_currencies
from .functions.sync_items import sync_items
from .config import ItemSyncConfig

# Add logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

headers = {"User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"}


async def run(config: ItemSyncConfig):
    await BaseRepository.init_pool(config.dbstring)
    with Client(headers=headers) as client:
        while True:
            logger.info("Fetching unique items from POE API...")
            response = client.get(config.unique_item_url)
            items: ItemResponse = ItemResponse(**response.json())
            logger.info(
                f"Retrieved {sum(len(cat.entries) for cat in items.result)} unique items " +\
                f"across {len(items.result)} categories"
            )

            logger.info("Fetching currency items from POE API...")
            response = client.get(config.currency_item_url)
            currencies: CurrencyResponse = CurrencyResponse(**response.json())
            logger.info(
                f"Retrieved {sum(len(cat.entries) for cat in currencies.result)} currency items "+\
                f"across {len(currencies.result)} categories"
            )

            logger.info("Starting item sync...")

            # TODO: Add all games
            await sync_items(items.result, constants.poe2_game_id)
            logger.info("Starting currency sync...")
            await sync_currencies(currencies.result, constants.poe2_game_id)
            await sleep(60 * 60 * 24)

