import sys
import asyncio

from services.itemSyncService.service import run
from services.itemSyncService.config import ItemSyncConfig
from dotenv import load_dotenv

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    load_dotenv()
    config = ItemSyncConfig.load_from_env()
    asyncio.run(run(config))
