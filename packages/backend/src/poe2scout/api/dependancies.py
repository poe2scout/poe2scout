import os
from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Annotated, Any, get_type_hints

from fastapi import Depends, Query
from pydantic import TypeAdapter
from redis import asyncio as aioredis

from poe2scout.db.repositories.currency_exchange_repository import (
    CurrencyExchangeRepository,
)
from poe2scout.db.repositories.item_repository import ItemRepository
from poe2scout.db.repositories.league_repository import LeagueRepository
from poe2scout.db.repositories.currency_item_repository import CurrencyItemRepository
from poe2scout.db.repositories.unique_item_repository import UniqueItemRepository
from poe2scout.db.repositories.price_log_repository import PriceLogRepository


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



_item_repository = ItemRepository()
def get_item_repository() -> ItemRepository:
    return _item_repository
ItemRepoDep = Annotated[ItemRepository, Depends(get_item_repository)]

_currency_exchange_repository = CurrencyExchangeRepository()
def get_currency_exchange_repo() -> CurrencyExchangeRepository:
    return _currency_exchange_repository
CXRepoDep = Annotated[CurrencyExchangeRepository, Depends(get_currency_exchange_repo)]

_currency_item_repository = CurrencyItemRepository()
def get_currency_item_repository() -> CurrencyItemRepository:
    return _currency_item_repository
CurrencyItemRepoDep = Annotated[CurrencyItemRepository, Depends(get_currency_item_repository)]

_league_repository = LeagueRepository()
def get_league_repo() -> LeagueRepository:
    return _league_repository
LeagueRepoDep = Annotated[LeagueRepository, Depends(get_league_repo)]

_price_log_repository = PriceLogRepository()
def get_price_log_repo() -> PriceLogRepository:
    return _price_log_repository
PriceLogRepoDep = Annotated[PriceLogRepository, Depends(get_price_log_repo)]

_unique_item_repository = UniqueItemRepository()
def get_unique_item_repo() -> UniqueItemRepository:
    return _unique_item_repository
UniqueItemRepoDep = Annotated[UniqueItemRepository, Depends(get_unique_item_repo)]

_economy_cache: EconomyCache = EconomyCache(
    _item_repository,
    _unique_item_repository,
    _currency_item_repository,
    _price_log_repository,
    _league_repository
)

EconomyCacheDep = Annotated[EconomyCache, Depends(get_economy_cache)]
