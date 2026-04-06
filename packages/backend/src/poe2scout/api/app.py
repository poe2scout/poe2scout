from contextlib import asynccontextmanager
import asyncio
import logging
import os
import sys
import time
from typing import AsyncIterator, cast

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from poe2scout.api.config import ApiServiceConfig
from poe2scout.api.routes import (
    items_router,
    leagues_router,
    root_static_router,
    static_router,
)
from poe2scout.db.repositories.base_repository import BaseRepository
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.types import ExceptionHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
config = ApiServiceConfig.load_from_env()
IS_LOCAL = os.getenv("LOCAL", "false").lower() == "true"


def get_real_ip(request: Request) -> str:
    real_ip = request.headers.get("cf-connecting-ip")

    if real_ip:
        return real_ip

    return get_remote_address(request)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    client_ip = get_real_ip(request)
    logger.warning(
        f"Custom Handler: Rate limit exceeded - IP: {client_ip}, "
        f"Path: {request.url.path}, "
        f"Method: {request.method}, "
        f"Limit Details: {exc.detail}"
    )

    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Limit: {exc.detail}. Please try again later.",
        },
    )

    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )

    return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await BaseRepository.init_pool(config.dbstring)
    yield


app = FastAPI(
    title="Jupiter Api",
    version="1.0",
    description="Jupiter Api",
    docs_url="/swagger",
    root_path="/api",
    lifespan=lifespan,
)

limiter = Limiter(
    key_func=get_real_ip, application_limits=["100/minute"], headers_enabled=True
)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    cast(ExceptionHandler, rate_limit_exceeded_handler),
)
app.add_middleware(SlowAPIMiddleware)

if IS_LOCAL:
    logger.info("Running in local mode, enabling CORS for localhost.")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Import and include routers
app.include_router(items_router)
app.include_router(leagues_router)
app.include_router(root_static_router)
app.include_router(static_router)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request details
    logger.info(f"Request started: {request.method} {request.url}")
    logger.info(f"Client IP: {request.client.host if request.client else 'Unknown'}")
    logger.info(f"Headers: {request.headers}")

    # Process the request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response details
    logger.info(f"Request completed: {request.method} {request.url}")
    logger.info(f"Status code: {response.status_code}")
    logger.info(f"Processing time: {process_time:.3f} seconds")

    return response


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=5000, proxy_headers=True, forwarded_allow_ips="*"
    )
