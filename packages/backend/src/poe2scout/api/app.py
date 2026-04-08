import asyncio
import sys

import uvicorn
from dotenv import load_dotenv

from poe2scout.api.application import create_app
from poe2scout.api.config import ApiServiceConfig
from poe2scout.observability.logging import configure_logging


load_dotenv()
config = ApiServiceConfig.load_from_env()
configure_logging(
    service_name=config.service_name,
    log_level=config.log_level,
    log_json=config.log_json,
)
app = create_app(config)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_config=None,
    )
