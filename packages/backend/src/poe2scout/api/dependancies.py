import os
from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Annotated, Any, get_type_hints

from fastapi import Depends, Query
from pydantic import TypeAdapter
from redis import asyncio as aioredis

from poe2scout.shared.pagination import PaginationParams

from .economy_cache import EconomyCache

redis = aioredis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    encoding="utf-8",
    decode_responses=True,
)

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

            cached_value = await redis.get(cache_key)
            if cached_value and type_adapter is not None:
                return type_adapter.validate_json(cached_value)

            response = await func(*args, **kwargs)

            if type_adapter is not None:
                json_response = type_adapter.dump_json(response).decode("utf-8")
                await redis.set(cache_key, json_response, ex=ttl)

            return response

        return wrapper

    return decorator


def get_economy_cache() -> EconomyCache:
    return _economy_cache

_economy_cache: EconomyCache = EconomyCache()

EconomyCacheDep = Annotated[EconomyCache, Depends(get_economy_cache)]
