from asyncio import gather
from typing import Annotated

from fastapi import Depends, HTTPException, Path

from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories import (
    currency_item_repository,
    league_repository,
    price_log_repository,
    realm_repository,
    unique_item_repository,
)

from .get import GetItemsResponse
from .. import router


class GetItemRequest(ApiModel):
    realm: str
    league_name: str
    item_id: int


def get_item_request(
    realm: Annotated[str, Path(alias="Realm")],
    league_name: Annotated[str, Path(alias="LeagueName")],
    item_id: Annotated[int, Path(alias="ItemId")],
) -> GetItemRequest:
    return GetItemRequest(
        realm=realm,
        league_name=league_name,
        item_id=item_id,
    )


GetItemRequestDep = Annotated[GetItemRequest, Depends(get_item_request)]


@router.get("/{LeagueName}/Items/{ItemId}")
async def get_item(
    request: GetItemRequestDep,
) -> GetItemsResponse:
    realm = await realm_repository.get_realm(request.realm)

    if realm is None:
        raise HTTPException(400, "Invalid realm")

    league, unique_item, currency_item = await gather(
        league_repository.get_league_by_value(request.league_name, realm.game_id),
        unique_item_repository.get_unique_item_by_item_id(request.item_id, realm.game_id),
        currency_item_repository.get_currency_item_by_item_id(request.item_id, realm.game_id),
    )

    if league is None:
        raise HTTPException(status_code=400, detail="League not found")

    item = unique_item or currency_item
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    price_logs = await price_log_repository.get_item_prices(
        [request.item_id],
        league.league_id,
        realm.realm_id,
    )
    current_price = price_logs[0].price if price_logs else 0

    if unique_item is not None:
        return GetItemsResponse.from_unique_item(unique_item, current_price)

    assert currency_item is not None
    return GetItemsResponse.from_currency_item(currency_item, current_price)
