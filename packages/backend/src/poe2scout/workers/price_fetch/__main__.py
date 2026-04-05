import sys
import asyncio
from datetime import datetime, timedelta
import logging
import dotenv

from poe2scout.db.repositories.currency_exchange_repository import (
    CurrencyExchangeRepository,
)
from poe2scout.db.repositories.currency_item_repository import CurrencyItemRepository
from poe2scout.db.repositories.league_repository import LeagueRepository
from poe2scout.db.repositories.price_log_repository import PriceLogRepository
from poe2scout.db.repositories.service_repository import ServiceRepository
from poe2scout.db.repositories.unique_item_repository import UniqueItemRepository
from .service import run
from .config import PriceFetchConfig
from poe2scout.db.repositories.base_repository import BaseRepository
from poe2scout.db.repositories.item_repository import ItemRepository

logger = logging.getLogger(__name__)


def calculate_poe_maintenance_time() -> float:
    """Calculate seconds until 10 minutes before next POE maintenance window (every 6 hours)"""
    current_time = datetime.now()
    hours_until_maintenance = 12 - (current_time.hour % 12)
    next_maintenance = current_time.replace(
        minute=0, second=0, microsecond=0
    ) + timedelta(hours=hours_until_maintenance)
    maintenance_warning = next_maintenance - timedelta(minutes=10)
    return (maintenance_warning - current_time).total_seconds()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    dotenv.load_dotenv()
    config = PriceFetchConfig.load_from_env()

    # Create maintenance timer with POE-specific maintenance schedule
    async def main_loop():
        await BaseRepository.init_pool(config.dbstring)
        item_repo = ItemRepository()
        currency_exchange_repo = CurrencyExchangeRepository()
        currency_item_repo = CurrencyItemRepository()
        league_repo = LeagueRepository()
        price_log_repo = PriceLogRepository()
        service_repo = ServiceRepository()
        unique_item_repo = UniqueItemRepository()

        while True:
            await run(
                config, 
                item_repo, 
                currency_item_repo,
                league_repo,
                price_log_repo,
                service_repo,
                currency_exchange_repo,
                unique_item_repo
            )

    # Single asyncio.run() call that manages the entire application lifecycle

    asyncio.run(main_loop(), debug=True)
