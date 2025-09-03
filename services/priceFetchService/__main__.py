import sys
import asyncio
import signal
from datetime import datetime, timedelta
import logging
from typing import Callable, Awaitable
from contextlib import asynccontextmanager
import dotenv
import time

from services.repositories.currency_exchange_repository import CurrencyExchangeRepository
from .service import run
from .config import PriceFetchConfig
from services.libs.MaintenanceTimer import MaintenanceTimer
from services.repositories.base_repository import BaseRepository
from services.repositories.item_repository import ItemRepository

logger = logging.getLogger(__name__)

def calculate_poe_maintenance_time() -> float:
    """Calculate seconds until 10 minutes before next POE maintenance window (every 6 hours)"""
    current_time = datetime.now()
    hours_until_maintenance = 12 - (current_time.hour % 12)
    next_maintenance = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=hours_until_maintenance)
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
        repo = ItemRepository()
        cxRepo = CurrencyExchangeRepository()
        print(config.dbstring)
        while True:
            await run(config, repo, cxRepo)

    # Single asyncio.run() call that manages the entire application lifecycle
    
    asyncio.run(main_loop(), debug=True)
