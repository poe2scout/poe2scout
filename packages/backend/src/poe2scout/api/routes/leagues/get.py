from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories import (
    currency_item_repository,
    league_repository,
    price_log_repository,
    realm_repository,
)
from . import router


class GetResponse(ApiModel):
    value: str
    divine_price: float
    chaos_divine_price: float

    @classmethod
    def from_model(
        cls,
        value: str,
        divine_price: float,
        chaos_divine_price: float,
    ) -> Self:
        return cls(
            value=value,
            divine_price=divine_price,
            chaos_divine_price=chaos_divine_price,
        )

class GetLeaguesRequest(ApiModel):
    realm: str

def get_leagues_request(
    realm: Annotated[str, Path(alias="Realm")]
) -> GetLeaguesRequest:
    return GetLeaguesRequest(
        realm=realm
    )

GetLeaguesRequestDep = Annotated[
    GetLeaguesRequest,
    Depends(get_leagues_request),
]

@router.get("")
async def get(
    request: GetLeaguesRequestDep
) -> list[GetResponse]:
    realm = await realm_repository.get_realm(request.realm)

    if realm is None:
        raise HTTPException(400, "Invalid realm")

    leagues = await league_repository.get_leagues(realm.game_id)

    divine_item = await currency_item_repository.get_divine_item(realm.game_id)

    chaos_item = await currency_item_repository.get_chaos_item(realm.game_id)

    responses: list[GetResponse] = []
    for league in leagues:
        divine_price = await price_log_repository.get_item_price(
            divine_item.item_id,
            league.league_id,
            realm.realm_id
        )
        chaos_price = await price_log_repository.get_item_price(
            chaos_item.item_id,
            league.league_id,
            realm.realm_id
        )

        responses.append(
            GetResponse.from_model(
                value=league.value,
                divine_price=divine_price if divine_price is not None else 50,
                chaos_divine_price=divine_price / chaos_price
                if chaos_price is not None
                else 50,
            )
        )

    return responses
