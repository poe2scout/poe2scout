import sys
import asyncio

from poe2scout.workers.item_sync.service import run
from poe2scout.workers.item_sync.config import ItemSyncConfig
from dotenv import load_dotenv

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    load_dotenv()
    config = ItemSyncConfig.load_from_env()
    asyncio.run(run(config), debug=True)
