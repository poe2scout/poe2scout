import sys
import asyncio
import signal
from datetime import datetime, timedelta
import logging
from typing import Callable, Awaitable
from contextlib import asynccontextmanager
import dotenv
import time
from .service import run
from .config import PriceFetchConfig
from services.libs.MaintenanceTimer import MaintenanceTimer
from services.repositories.base_repository import BaseRepository
from services.repositories.item_repository import ItemRepository

logger = logging.getLogger(__name__)

def calculate_poe_maintenance_time() -> float:
    """Calculate seconds until 10 minutes before next POE maintenance window (every 6 hours)"""
    current_time = datetime.now()
    hours_until_maintenance = 6 - (current_time.hour % 6)
    next_maintenance = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=hours_until_maintenance)
    maintenance_warning = next_maintenance - timedelta(minutes=10)
    return (maintenance_warning - current_time).total_seconds()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    dotenv.load_dotenv()
    config = PriceFetchConfig.load_from_env()

    # Create maintenance timer with POE-specific maintenance schedule
    timer = MaintenanceTimer(get_next_maintenance=calculate_poe_maintenance_time)

    async def main_loop():
        # Initialize DB connection pool once
        await BaseRepository.init_pool(config.dbstring)
        repo = ItemRepository()
        #pausing to let itemSyncService run first
        while True:
            try:
                async with timer:
                    logger.info("Starting maintenance timer")
                    await timer.run_cancellable(run(config, repo))
            except asyncio.CancelledError:
                logger.info("Service stopped for maintenance window, will restart after maintenance")
                logger.info("Sleeping for 15 minutes")
                await asyncio.sleep(900)  # Using asyncio.sleep instead of time.sleep
                continue

    # Single asyncio.run() call that manages the entire application lifecycle
    
    asyncio.run(main_loop())
