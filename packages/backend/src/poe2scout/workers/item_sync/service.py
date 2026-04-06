from poe2scout.db.repositories import game_repository
from poe2scout.db.repositories.base_repository import BaseRepository
import logging
from httpx import Client
from asyncio import sleep

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
            games = await game_repository.get_games()

            for game in games:
                logger.info("Fetching unique items from POE API...")
                response = client.get(f"https://www.pathofexile.com/api/{game.ggg_api_trade_identifier}/data/items")
                items: ItemResponse = ItemResponse(**response.json())
                logger.info(
                    f"Retrieved {sum(len(cat.entries) for cat in items.result)} unique items " +\
                    f"across {len(items.result)} categories"
                )

                logger.info("Fetching currency items from POE API...")
                response = client.get(f"https://www.pathofexile.com/api/{game.ggg_api_trade_identifier}/data/static")
                currencies: CurrencyResponse = CurrencyResponse(**response.json())
                logger.info(
                    f"Retrieved {sum(len(cat.entries) for cat in currencies.result)} " +\
                    f"currency items across {len(currencies.result)} categories"
                )

                logger.info("Starting item sync...")
                await sync_items(items.result, game)
                logger.info("Starting currency sync...")
                await sync_currencies(currencies.result, game.game_id)
            await sleep(60 * 60 * 24)

