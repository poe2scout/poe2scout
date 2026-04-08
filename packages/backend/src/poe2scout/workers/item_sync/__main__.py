import sys
import asyncio

from dotenv import load_dotenv
from httpx import Client

from poe2scout.db.repositories.base_repository import BaseRepository
from poe2scout.observability.logging import configure_logging
from poe2scout.observability.worker_runner import ServiceRunner
from poe2scout.workers.item_sync.config import ItemSyncConfig
from poe2scout.workers.item_sync.service import headers, run_once

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    load_dotenv()
    config = ItemSyncConfig.load_from_env()
    configure_logging(
        service_name=config.service_name,
        log_level=config.log_level,
        log_json=config.log_json,
    )

    async def main() -> None:
        await BaseRepository.init_pool(config.dbstring)
        runner = ServiceRunner(
            service_name=config.service_name,
            metrics_port=config.metrics_port,
            expected_interval_seconds=config.expected_interval_seconds,
        )
        with Client(headers=headers) as client:
            await runner.run_forever(
                lambda: run_once(client),
                backoff_initial_seconds=config.backoff_initial_seconds,
                backoff_max_seconds=config.backoff_max_seconds,
            )

    asyncio.run(main())
