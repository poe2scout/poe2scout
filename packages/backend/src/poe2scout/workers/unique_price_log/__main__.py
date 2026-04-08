import sys
import asyncio
import dotenv

from .service import fetch_prices
from .config import PriceFetchConfig
from poe2scout.db.repositories.base_repository import BaseRepository
from poe2scout.integrations.poe.client import PoeTradeClient
from poe2scout.observability.logging import configure_logging
from poe2scout.observability.worker_runner import ServiceRunner


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    dotenv.load_dotenv()
    config = PriceFetchConfig.load_from_env()
    configure_logging(
        service_name=config.service_name,
        log_level=config.log_level,
        log_json=config.log_json,
    )

    async def main_loop() -> None:
        await BaseRepository.init_pool(config.dbstring)
        runner = ServiceRunner(
            service_name=config.service_name,
            metrics_port=config.metrics_port,
            expected_interval_seconds=config.expected_interval_seconds,
        )
        headers = {"User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"}
        async with PoeTradeClient(headers=headers) as client:
            await runner.run_forever(
                lambda: fetch_prices(client),
                backoff_initial_seconds=config.backoff_initial_seconds,
                backoff_max_seconds=config.backoff_max_seconds,
            )

    asyncio.run(main_loop())
