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
    base_currency_api_id: str
    base_currency_text: str
    base_currency_icon_url: str | None
    exalted_currency_text: str
    exalted_currency_icon_url: str | None
    divine_currency_text: str
    divine_currency_icon_url: str | None
    chaos_currency_text: str
    chaos_currency_icon_url: str | None

    @classmethod
    def from_model(
        cls,
        value: str,
        divine_price: float,
        chaos_divine_price: float,
        base_currency_api_id: str,
        base_currency_text: str,
        base_currency_icon_url: str | None,
        exalted_currency_text: str,
        exalted_currency_icon_url: str | None,
        divine_currency_text: str,
        divine_currency_icon_url: str | None,
        chaos_currency_text: str,
        chaos_currency_icon_url: str | None,
    ) -> Self:
        return cls(
            value=value,
            divine_price=divine_price,
            chaos_divine_price=chaos_divine_price,
            base_currency_api_id=base_currency_api_id,
            base_currency_text=base_currency_text,
            base_currency_icon_url=base_currency_icon_url,
            exalted_currency_text=exalted_currency_text,
            exalted_currency_icon_url=exalted_currency_icon_url,
            divine_currency_text=divine_currency_text,
            divine_currency_icon_url=divine_currency_icon_url,
            chaos_currency_text=chaos_currency_text,
            chaos_currency_icon_url=chaos_currency_icon_url,
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

    exalted_item = await currency_item_repository.get_exalted_item(realm.game_id)
    divine_item = await currency_item_repository.get_divine_item(realm.game_id)
    chaos_item = await currency_item_repository.get_chaos_item(realm.game_id)
    icon_lookup = {
        exalted_item.api_id: exalted_item.icon_url,
        divine_item.api_id: divine_item.icon_url,
        chaos_item.api_id: chaos_item.icon_url,
    }

    responses: list[GetResponse] = []
    for league in leagues:
        divine_price = await price_log_repository.get_item_price(
            divine_item.item_id,
            league.league_id,
            realm.realm_id,
            None
        )
        chaos_price = await price_log_repository.get_item_price(
            chaos_item.item_id,
            league.league_id,
            realm.realm_id,
            None
        )

        responses.append(
            GetResponse.from_model(
                value=league.value,
                divine_price=divine_price if divine_price is not None else 50,
                chaos_divine_price=divine_price / chaos_price
                if chaos_price is not None and chaos_price != 0
                else 50,
                base_currency_api_id=league.base_currency_api_id,
                base_currency_text=league.base_currency_text,
                base_currency_icon_url=icon_lookup.get(league.base_currency_api_id),
                exalted_currency_text=exalted_item.text,
                exalted_currency_icon_url=exalted_item.icon_url,
                divine_currency_text=divine_item.text,
                divine_currency_icon_url=divine_item.icon_url,
                chaos_currency_text=chaos_item.text,
                chaos_currency_icon_url=chaos_item.icon_url,
            )
        )

    return responses
