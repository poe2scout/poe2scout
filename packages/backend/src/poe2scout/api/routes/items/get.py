from asyncio import gather
from typing import Annotated, Self

from cachetools import TTLCache
from cachetools.keys import hashkey
from fastapi import Depends, Path

from poe2scout.api.api_model import ApiModel
from poe2scout.api.dependancies import LeagueContextDep
from poe2scout.db.repositories import (
    currency_item_repository,
    price_log_repository,
    unique_item_repository,
)
from poe2scout.db.repositories.unique_item_repository.get_all_unique_items import UniqueItem
from poe2scout.db.repositories.models import CurrencyItem

from . import router

items_cache = TTLCache(maxsize=1, ttl=60 * 15)


class GetItemsRequest(ApiModel):
    realm: str
    league_name: str


def get_items_request(
    realm: Annotated[str, Path(alias="Realm")],
    league_name: Annotated[str, Path(alias="LeagueName")],
) -> GetItemsRequest:
    return GetItemsRequest(realm=realm, league_name=league_name)


GetItemsRequestDep = Annotated[GetItemsRequest, Depends(get_items_request)]


class GetItemsResponse(ApiModel):
    item_id: int
    category_api_id: str
    text: str
    name: str | None = None
    type: str | None = None
    api_id: str | None = None
    current_price: float
    icon_url: str | None

    @classmethod
    def from_unique_item(
        cls, item: UniqueItem, current_price: float
    ) -> Self:
        return cls(
            item_id=item.item_id,
            category_api_id=item.category_api_id,
            text=item.text,
            name=item.name,
            type=item.type,
            api_id=None,
            current_price=current_price,
            icon_url=item.icon_url,
        )

    @classmethod
    def from_currency_item(
        cls, item: CurrencyItem, current_price: float
    ) -> Self:
        return cls(
            item_id=item.item_id,
            category_api_id=item.category_api_id,
            text=item.text,
            name=None,
            type=None,
            api_id=item.api_id,
            current_price=current_price,
            icon_url=item.icon_url,
        )



@router.get("")
async def get_items(
    request: GetItemsRequestDep,
    context: LeagueContextDep,
) -> list[GetItemsResponse]:
    cache_key = hashkey(request.league_name, request.realm)

    if cache_key in items_cache:
        return items_cache[cache_key]

    realm = context.realm
    league = context.league

    unique_items, currency_items = await gather(
        unique_item_repository.get_all_unique_items(realm.game_id),
        currency_item_repository.get_all_currency_items(realm.game_id),
    )

    item_ids = [item.item_id for item in unique_items] + [
        item.item_id for item in currency_items
    ]

    price_logs_by_item_id = await price_log_repository.get_item_prices(
        item_ids,
        league.league_id,
        realm.realm_id,
    )

    current_price_dict = {
        current_price.item_id: current_price.price
        for current_price in price_logs_by_item_id
    }

    responses = [
        GetItemsResponse.from_unique_item(
            item,
            current_price_dict.get(item.item_id, 0),
        )
        for item in unique_items
    ] + [
        GetItemsResponse.from_currency_item(
            item,
            current_price_dict.get(item.item_id, 0),
        )
        for item in currency_items
    ]

    items_cache[cache_key] = responses
    return responses
