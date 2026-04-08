from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Awaitable, Callable, cast
from uuid import uuid4

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CollectorRegistry
from slowapi import Limiter
from slowapi.extension import StrOrCallableStr
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.routing import Match
from starlette.types import ExceptionHandler

from poe2scout.api.config import ApiServiceConfig
from poe2scout.api.dependancies import cache_response, close_redis_client, redis_ping
from poe2scout.api.routes import (
    items_router,
    leagues_router,
    root_static_router,
    static_router,
)
from poe2scout.db.repositories.base_repository import BaseRepository
from poe2scout.observability.context import request_context
from poe2scout.observability.metrics import ApiMetrics, create_registry
from poe2scout.observability.metrics_server import MetricsServer


logger = logging.getLogger(__name__)


AsyncDependencyCheck = Callable[[], Awaitable[bool]]


@dataclass
class ApiDependencyChecks:
    db: AsyncDependencyCheck
    redis: AsyncDependencyCheck


def get_real_ip(request: Request) -> str:
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.client.host if request.client else "unknown"


def hash_client_ip(raw_ip: str, secret_key: str) -> str:
    digest = hashlib.sha256(f"{secret_key}:{raw_ip}".encode("utf-8")).hexdigest()
    return digest[:16]


def get_route_template(request: Request) -> str:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    if route_path:
        return route_path

    for candidate_route in request.app.router.routes:
        match, _child_scope = candidate_route.matches(request.scope)
        candidate_path = getattr(candidate_route, "path", None)
        if match == Match.FULL and candidate_path:
            return candidate_path

    return "unmatched"


def default_dependency_checks() -> ApiDependencyChecks:
    async def db_check() -> bool:
        async with asyncio.timeout(2):
            async with BaseRepository.get_db_cursor() as cursor:
                await cursor.execute("SELECT 1")
                row = await cursor.fetchone()
                return row is not None

    async def redis_check() -> bool:
        return await redis_ping(timeout_seconds=2)

    return ApiDependencyChecks(db=db_check, redis=redis_check)


async def evaluate_readiness(
    dependency_checks: ApiDependencyChecks,
    metrics: ApiMetrics,
) -> dict[str, str]:
    checks: dict[str, str] = {}
    for dependency_name, dependency_check in (
        ("db", dependency_checks.db),
        ("redis", dependency_checks.redis),
    ):
        try:
            ok = await dependency_check()
        except Exception:
            ok = False
        metrics.set_readiness(dependency_name, ok)
        checks[dependency_name] = "ok" if ok else "error"

    return checks


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    request_context_state = getattr(request.state, "request_context", None)
    if request_context_state is not None:
        request_context_state.rate_limited = True
        request_context_state.exception_type = type(exc).__name__

    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Limit: {exc.detail}. Please try again later.",
        },
    )
    response = request.app.state.limiter._inject_headers(response, request.state.view_rate_limit)
    return response


def create_app(
    config: ApiServiceConfig,
    *,
    dependency_checks: ApiDependencyChecks | None = None,
    application_limits: list[StrOrCallableStr] | None = None,
    registry: CollectorRegistry | None = None,
    enable_test_routes: bool = False,
    initialize_database_pool: bool = True,
    start_metrics_server: bool = True,
) -> FastAPI:
    dependency_checks = dependency_checks or default_dependency_checks()
    metrics_registry = registry or create_registry()
    api_metrics = ApiMetrics(config.service_name, metrics_registry)
    os.environ["REDIS_URL"] = config.redis_url

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if initialize_database_pool:
            await BaseRepository.init_pool(config.dbstring)
        metrics_server = MetricsServer(registry=metrics_registry, port=config.metrics_port)
        if start_metrics_server:
            metrics_server.start()

        async def readiness_loop() -> None:
            while True:
                await evaluate_readiness(dependency_checks, api_metrics)
                await asyncio.sleep(config.readiness_poll_interval_seconds)

        readiness_task = asyncio.create_task(readiness_loop())
        try:
            yield
        finally:
            readiness_task.cancel()
            try:
                await readiness_task
            except asyncio.CancelledError:
                pass
            if start_metrics_server:
                metrics_server.stop()
            await close_redis_client()
            if initialize_database_pool:
                await BaseRepository.close_pool()

    app = FastAPI(
        title="POE2 Scout API",
        version="1.0",
        description="POE2 Scout API",
        docs_url="/swagger",
        root_path="/api",
        lifespan=lifespan,
    )

    limiter = Limiter(
        key_func=get_real_ip,
        application_limits=application_limits or ["100/minute"],
        headers_enabled=True,
    )
    app.state.limiter = limiter
    app.state.api_metrics = api_metrics
    app.state.api_config = config
    app.state.metrics_registry = metrics_registry
    app.state.readiness_dependency_checks = dependency_checks
    app.add_exception_handler(
        RateLimitExceeded,
        cast(ExceptionHandler, rate_limit_exceeded_handler),
    )
    app.add_middleware(SlowAPIMiddleware)

    if config.local:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(items_router)
    app.include_router(leagues_router)
    app.include_router(root_static_router)
    app.include_router(static_router)

    @app.middleware("http")
    async def observe_requests(request: Request, call_next):
        start_time = time.perf_counter()
        request_id = request.headers.get("x-request-id") or str(uuid4())
        method = request.method
        client_ip_hash = hash_client_ip(get_real_ip(request), config.secret_key)
        api_metrics.track_in_flight()

        with request_context(request) as current_request_context:
            request.state.request_context = current_request_context
            response = None
            status_code = 500
            try:
                response = await call_next(request)
                status_code = response.status_code
                response.headers["X-Request-ID"] = request_id
                return response
            except Exception as exc:
                current_request_context.exception_type = type(exc).__name__
                logger.exception(
                    "request raised an exception",
                    extra={
                        "event": "http_request_exception",
                        "service": config.service_name,
                        "request_id": request_id,
                        "method": method,
                        "route_template": get_route_template(request),
                        "client_ip_hash": client_ip_hash,
                        "exception_type": type(exc).__name__,
                    },
                )
                raise
            finally:
                route_template = get_route_template(request)
                duration_seconds = time.perf_counter() - start_time
                duration_ms = round(duration_seconds * 1000, 3)
                rate_limited = current_request_context.rate_limited or status_code == 429
                api_metrics.observe_request(
                    method=method,
                    route_template=route_template,
                    status_code=status_code,
                    duration_seconds=duration_seconds,
                    slow_threshold_seconds=config.slow_request_threshold_ms / 1000,
                    rate_limited=rate_limited,
                )
                api_metrics.finish_in_flight()
                logger.info(
                    "request completed",
                    extra={
                        "event": "http_request_completed",
                        "service": config.service_name,
                        "request_id": request_id,
                        "method": method,
                        "route_template": route_template,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "client_ip_hash": client_ip_hash,
                        "cache_status": current_request_context.cache_status,
                        "rate_limited": rate_limited,
                        "exception_type": current_request_context.exception_type,
                    },
                )

    @app.get("/health/live")
    @limiter.exempt
    async def health_live() -> dict[str, str]:
        return {"status": "ok", "service": config.service_name}

    @app.get("/health/ready")
    @limiter.exempt
    async def health_ready() -> JSONResponse:
        checks = await evaluate_readiness(dependency_checks, api_metrics)
        status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
        status_code = 200 if status == "ok" else 503
        return JSONResponse(
            status_code=status_code,
            content={
                "status": status,
                "service": config.service_name,
                "checks": checks,
            },
        )

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"message": "Hello World"}

    if enable_test_routes:
        test_router = APIRouter(prefix="/_test", tags=["Testing"])

        @test_router.get("/ok")
        async def test_ok() -> dict[str, str]:
            return {"status": "ok"}

        @test_router.get("/bad-request")
        async def test_bad_request() -> Response:
            raise HTTPException(status_code=400, detail="bad request")

        @test_router.get("/error")
        async def test_error() -> Response:
            raise RuntimeError("boom")

        @test_router.get("/slow")
        async def test_slow() -> dict[str, str]:
            await asyncio.sleep(0.05)
            return {"status": "slow"}

        @test_router.get("/cached")
        @cache_response(key=lambda _params: "test-cached", ttl=60)
        async def test_cached() -> dict[str, str]:
            return {"status": "cached"}

        app.include_router(test_router)

    return app
