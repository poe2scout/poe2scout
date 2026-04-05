from asyncio import gather
from datetime import datetime
from typing import Annotated, Self

from cachetools import TTLCache
from cachetools.keys import hashkey
from fastapi import Depends, HTTPException, Path

from poe2scout.api.dependancies import ItemRepoDep
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories.item_repository.get_all_unique_items import UniqueItem
from poe2scout.db.repositories.models import CurrencyItem, PriceLogEntry

from . import router

items_cache = TTLCache(maxsize=1, ttl=60 * 15)


class GetItemsRequest(ApiModel):
    league_name: str


def get_items_request(
    league_name: Annotated[str, Path(alias="LeagueName")],
) -> GetItemsRequest:
    return GetItemsRequest(league_name=league_name)


GetItemsRequestDep = Annotated[GetItemsRequest, Depends(get_items_request)]


class GetItemsResponse(ApiModel):
    class _PriceLogEntry(ApiModel):
        price: float
        time: datetime
        quantity: int

        @classmethod
        def from_model(cls, price_log: PriceLogEntry) -> Self:
            return cls(
                price=price_log.price,
                time=price_log.time,
                quantity=price_log.quantity,
            )

    item_id: int
    category_api_id: str
    text: str
    name: str | None = None
    type: str | None = None
    api_id: str | None = None
    price_logs: list[_PriceLogEntry | None]
    current_price: float
    icon_url: str | None

    @classmethod
    def from_unique_item(
        cls, item: UniqueItem, price_logs: list[PriceLogEntry | None]
    ) -> Self:
        return cls(
            item_id=item.item_id,
            category_api_id=item.category_api_id,
            text=item.text,
            name=item.name,
            type=item.type,
            api_id=None,
            price_logs=cls._map_price_logs(price_logs),
            current_price=cls._get_current_price(price_logs),
            icon_url=item.icon_url,
        )

    @classmethod
    def from_currency_item(
        cls, item: CurrencyItem, price_logs: list[PriceLogEntry | None]
    ) -> Self:
        return cls(
            item_id=item.item_id,
            category_api_id=item.category_api_id,
            text=item.text,
            name=None,
            type=None,
            api_id=item.api_id,
            price_logs=cls._map_price_logs(price_logs),
            current_price=cls._get_current_price(price_logs),
            icon_url=item.icon_url,
        )

    @classmethod
    def _map_price_logs(
        cls, price_logs: list[PriceLogEntry | None]
    ) -> list[_PriceLogEntry | None]:
        return [
            cls._PriceLogEntry.from_model(price_log)
            if price_log is not None
            else None
            for price_log in price_logs
        ]

    @staticmethod
    def _get_current_price(price_logs: list[PriceLogEntry | None]) -> float:
        return next(
            (price_log.price for price_log in price_logs if price_log is not None),
            0,
        )


@router.get("/{LeagueName}/Items")
async def get_items(
    request: GetItemsRequestDep,
    item_repository: ItemRepoDep,
) -> list[GetItemsResponse]:
    cache_key = hashkey(request.league_name)

    if cache_key in items_cache:
        return items_cache[cache_key]

    unique_items, currency_items, leagues = await gather(
        item_repository.get_all_unique_items(),
        item_repository.get_all_currency_items(),
        item_repository.get_all_leagues(),
    )

    item_ids = [item.item_id for item in unique_items] + [
        item.item_id for item in currency_items
    ]

    league_id = next(
        (league.league_id for league in leagues if league.value == request.league_name),
        None,
    )

    if league_id is None:
        raise HTTPException(status_code=404, detail="League not found")

    price_logs_by_item_id = await item_repository.get_item_price_logs(item_ids, league_id)

    responses = [
        GetItemsResponse.from_unique_item(
            item,
            price_logs_by_item_id.get(item.item_id, []),
        )
        for item in unique_items
    ] + [
        GetItemsResponse.from_currency_item(
            item,
            price_logs_by_item_id.get(item.item_id, []),
        )
        for item in currency_items
    ]

    items_cache[cache_key] = responses
    return responses
