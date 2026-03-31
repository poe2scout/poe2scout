from fastapi import Query, Depends
from typing import Annotated, get_type_hints, Callable
from pydantic import BaseModel
from functools import wraps
from redis import asyncio as aioredis
import os
from services.libs.models.PaginationParams import PaginationParams
from services.repositories import ItemRepository
from pydantic import TypeAdapter
from .EconomyCache import EconomyCache

from services.repositories.currency_exchange_repository import (
    CurrencyExchangeRepository,
)

redis = aioredis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    encoding="utf-8",
    decode_responses=True,
)


def get_pagination_params(
    page: int = Query(default=1, ge=1, description="Page number"),
    perPage: int = Query(default=25, ge=1, le=250, description="Items per page"),
    league: str = Query(default="Standard", description="League name"),
) -> PaginationParams:
    return PaginationParams(page=page, perPage=perPage, league=league)


def get_item_repository() -> ItemRepository:
    return _item_repository


_item_repository = ItemRepository()


def get_cx_repo() -> CurrencyExchangeRepository:
    return _cx_repository


_cx_repository = CurrencyExchangeRepository()

CXRepoDep = Annotated[CurrencyExchangeRepository, Depends(get_cx_repo)]
ItemRepoDep = Annotated[ItemRepository, Depends(get_item_repository)]


class PaginatedResponse(BaseModel):
    currentPage: int
    pages: int
    total: int


def cache_response(key: Callable, ttl: int = 300):
    """
    Caching decorator for FastAPI endpoints that handles Pydantic models.

    Args:
        key: Either a static string key or a function that generates the key from the endpoint parameters
        ttl: Time to live for the cache in seconds
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = key(kwargs)
            cached_value = None  # await redis.get(cache_key)
            if cached_value:
                return_type = get_type_hints(func).get("return")
                type_adapter = TypeAdapter(return_type)
                return type_adapter.validate_json(cached_value)

            response = await func(*args, **kwargs)
            json_response = response.model_dump_json()
            await redis.set(cache_key, json_response, ex=ttl)
            return response

        return wrapper

    return decorator


def get_economy_cache() -> EconomyCache:
    return _economy_cache


_economy_cache: EconomyCache = EconomyCache(_item_repository)

EconomyCacheDep = Annotated[EconomyCache, Depends(get_economy_cache)]
