import asyncio
import logging
import sys

import dotenv

from poe2scout.db.repositories.currency_item_repository import CurrencyItemRepository
from poe2scout.db.repositories.league_repository import LeagueRepository
from poe2scout.db.repositories.price_log_repository import PriceLogRepository
from poe2scout.db.repositories.service_repository import ServiceRepository
from poe2scout.workers.currency_exchange.config import CurrencyExchangeServiceConfig
from poe2scout.integrations.poe.client import PoeApiClient
from poe2scout.db.repositories.base_repository import BaseRepository
from poe2scout.db.repositories.currency_exchange_repository import (
    CurrencyExchangeRepository,
)
from poe2scout.db.repositories.item_repository import ItemRepository
from poe2scout.workers.currency_exchange.service import run


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    dotenv.load_dotenv()
    config = CurrencyExchangeServiceConfig.load_from_env()

    async def main_loop():
        await BaseRepository.init_pool(config.dbstring)
        item_repo = ItemRepository()
        currency_exchange_repo = CurrencyExchangeRepository()
        price_log_repo = PriceLogRepository()
        league_repo = LeagueRepository()
        currency_item_repo = CurrencyItemRepository()
        service_repo = ServiceRepository()

        async with PoeApiClient(
            config.POEAPI_CLIENT_ID, config.POEAPI_CLIENT_SECRET
        ) as client:
            while True:
                await run(
                    config, 
                    item_repo, 
                    currency_exchange_repo, 
                    service_repo,
                    league_repo,
                    price_log_repo,
                    currency_item_repo,
                    client
                )
                await asyncio.sleep(15)

    asyncio.run(main_loop())
