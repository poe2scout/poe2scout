import asyncio
import requests
from services.repositories.base_repository import BaseRepository
from services.itemSyncService.models import *
import logging
import json
from httpx import Client
from asyncio import sleep
from .functions.sync_currencies import sync_currencies
from .functions.sync_items import sync_items
from .config import ItemSyncConfig
from services.repositories import ItemRepository
# Add logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

headers = {
    'User-Agent': 'POE2SCOUT (contact: b@girardet.co.nz)'
}


async def run(config: ItemSyncConfig):
    has_run = 0
    with Client(headers=headers) as client:
        while True:
            if has_run == 0:
                has_run = 1
                await asyncio.sleep(60*10)
            await BaseRepository.init_pool(config.dbstring)
            repo = ItemRepository()

            logger.info("Fetching unique items from POE API...")
            response = client.get(config.unique_item_url)
            items: itemResponse = itemResponse(**response.json())
            logger.info(
                f"Retrieved {sum(len(cat.entries) for cat in items.result)} unique items across {len(items.result)} categories")

            logger.info("Fetching currency items from POE API...")
            response = client.get(config.currency_item_url)
            currencies: currencyResponse = currencyResponse(**response.json())
            logger.info(
                f"Retrieved {sum(len(cat.entries) for cat in currencies.result)} currency items across {len(currencies.result)} categories")

            logger.info("Starting item sync...")
            await sync_items(items.result)
            logger.info("Starting currency sync...")
            await sync_currencies(currencies.result)

            await sleep(60 * 60 * 24)
