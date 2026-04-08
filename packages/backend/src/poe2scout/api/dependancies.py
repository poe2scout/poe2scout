import asyncio
import logging
import os
from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Annotated, Any, get_type_hints

from fastapi import Depends, Query
from pydantic import TypeAdapter
from redis import asyncio as aioredis

from poe2scout.observability.context import get_current_request_context
from poe2scout.shared.pagination import PaginationParams

from .economy_cache import EconomyCache

logger = logging.getLogger(__name__)

_redis_client = None
_redis_url = None


def get_redis_client():
    global _redis_client
    global _redis_url

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    if _redis_client is None or _redis_url != redis_url:
        _redis_client = aioredis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        _redis_url = redis_url

    return _redis_client


async def close_redis_client() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


async def redis_ping(timeout_seconds: float = 2.0) -> bool:
    return bool(await asyncio.wait_for(get_redis_client().ping(), timeout=timeout_seconds))


def _record_cache_result(result: str) -> None:
    request_context = get_current_request_context()
    if request_context is None:
        return

    request_context.cache_status = result
    api_metrics = getattr(request_context.request.app.state, "api_metrics", None)
    if api_metrics is not None:
        api_metrics.record_cache(result)


def get_pagination_params(
    page: int = Query(default=1, ge=1, description="Page number", alias="Page"),
    per_page: int = Query(
        default=25,
        ge=1,
        le=250,
        description="Items per page",
        alias="PerPage",
    ),
) -> PaginationParams:
    return PaginationParams(page=page, per_page=per_page)


PaginationParamDep = Annotated[PaginationParams, Depends(get_pagination_params)]


def cache_response(key: Callable[[dict[str, Any]], str], ttl: int = 300):
    """
    Caching decorator for FastAPI endpoints that handles Pydantic models.

    Args:
        key: Function that generates a cache key from the endpoint parameters.
        ttl: Time to live for the cache in seconds
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return_type = get_type_hints(func).get("return")
        type_adapter = TypeAdapter(return_type) if return_type is not None else None

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound_arguments = signature(func).bind_partial(*args, **kwargs)
            bound_arguments.apply_defaults()
            cache_key = key(dict(bound_arguments.arguments))

            try:
                cached_value = await get_redis_client().get(cache_key)
            except Exception:
                _record_cache_result("error")
                logger.warning(
                    "redis cache read failed",
                    extra={"event": "redis_cache_read_failed", "cache_key": cache_key},
                )
                cached_value = None
            else:
                if cached_value and type_adapter is not None:
                    _record_cache_result("hit")
                    return type_adapter.validate_json(cached_value)

            _record_cache_result("miss")

            response = await func(*args, **kwargs)

            if type_adapter is not None:
                json_response = type_adapter.dump_json(response).decode("utf-8")
                try:
                    await get_redis_client().set(cache_key, json_response, ex=ttl)
                except Exception:
                    logger.warning(
                        "redis cache write failed",
                        extra={"event": "redis_cache_write_failed", "cache_key": cache_key},
                    )

            return response

        return wrapper

    return decorator


def get_economy_cache() -> EconomyCache:
    return _economy_cache


_economy_cache: EconomyCache = EconomyCache()

EconomyCacheDep = Annotated[EconomyCache, Depends(get_economy_cache)]
