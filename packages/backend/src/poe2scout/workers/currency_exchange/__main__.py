import asyncio
import logging
import sys

import dotenv

from poe2scout.workers.currency_exchange.config import CurrencyExchangeServiceConfig
from poe2scout.integrations.poe.client import PoeApiClient
from poe2scout.db.repositories.base_repository import BaseRepository
from poe2scout.workers.currency_exchange.service import run


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    dotenv.load_dotenv()
    config = CurrencyExchangeServiceConfig.load_from_env()

    async def main_loop():
        await BaseRepository.init_pool(config.dbstring)

        async with PoeApiClient(
            config.POEAPI_CLIENT_ID, config.POEAPI_CLIENT_SECRET
        ) as client:
            while True:
                await run(config, client)

    asyncio.run(main_loop())
