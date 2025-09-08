
import asyncio
import logging
import sys

import dotenv

from services.currencyExchangeService.config import CurrencyExchangeServiceConfig
from services.libs.poe_trade_client import PoeApiClient
from services.repositories.base_repository import BaseRepository
from services.repositories.currency_exchange_repository import CurrencyExchangeRepository
from services.repositories.item_repository import ItemRepository
from services.currencyExchangeService.service import run


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    dotenv.load_dotenv()
    config = CurrencyExchangeServiceConfig.load_from_env()

    async def main_loop():
        await BaseRepository.init_pool(config.dbstring)
        itemRepo = ItemRepository()
        cxRepo = CurrencyExchangeRepository()
        async with PoeApiClient(config.POEAPI_CLIENT_ID, config.POEAPI_CLIENT_SECRET) as client:
            while True:
                await run(config, itemRepo, cxRepo, client)
                await asyncio.sleep(15)
    
    asyncio.run(main_loop())
