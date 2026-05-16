from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories import (
    currency_item_repository,
    league_repository,
    price_log_repository,
    realm_repository,
)
from poe2scout.db.repositories.league_repository.get_leagues import League
from poe2scout.db.repositories.models import CurrencyItem
from . import router




class GetResponse(ApiModel):
    value: str
    short_name: str
    is_current: bool
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
    default_currency: LeagueCurrency

    class LeagueCurrency(ApiModel):
        api_id: str
        text: str
        icon_url: str | None
        relative_price: float

        @classmethod
        def from_model(
            cls,
            model: BaseCurrency,
            relative_price: float,
        ) -> Self:
            if isinstance(model, League):
                return cls(
                    api_id=model.base_currency_api_id,
                    text=model.base_currency_text,
                    icon_url=model.base_currency_icon_url,
                    relative_price=relative_price,
                )

            return cls(
                api_id=model.api_id,
                text=model.text,
                icon_url=model.icon_url,
                relative_price=relative_price,
            )


    @classmethod
    def from_model(
        cls,
        league: League,
        exalted_item: CurrencyItem,
        divine_item: CurrencyItem,
        chaos_item: CurrencyItem,
        price_lookup: dict[tuple[int, int], float],
    ) -> Self:
        default_currency = GetResponse.LeagueCurrency.from_model(league, relative_price=1)
        divine_price = price_lookup.get((league.league_id, divine_item.item_id), 0)
        chaos_price = price_lookup.get((league.league_id, chaos_item.item_id), 0)

        return cls(
            value=league.value,
            short_name=league.short_name,
            is_current=league.current_league,
            divine_price=divine_price,
            chaos_divine_price=divine_price / chaos_price if chaos_price != 0 else 50,
            base_currency_api_id=league.base_currency_api_id,
            base_currency_text=league.base_currency_text,
            base_currency_icon_url=league.base_currency_icon_url,
            exalted_currency_text=exalted_item.text,
            exalted_currency_icon_url=exalted_item.icon_url,
            divine_currency_text=divine_item.text,
            divine_currency_icon_url=divine_item.icon_url,
            chaos_currency_text=chaos_item.text,
            chaos_currency_icon_url=chaos_item.icon_url,
            default_currency=default_currency,
        )


class GetLeaguesRequest(ApiModel):
    realm: str


def get_leagues_request(realm: Annotated[str, Path(alias="Realm")]) -> GetLeaguesRequest:
    return GetLeaguesRequest(realm=realm)


GetLeaguesRequestDep = Annotated[
    GetLeaguesRequest,
    Depends(get_leagues_request),
]


@router.get("")
async def get(request: GetLeaguesRequestDep) -> list[GetResponse]:
    realm = await realm_repository.get_realm(request.realm)

    if realm is None:
        raise HTTPException(400, "Invalid realm")

    leagues = await league_repository.get_leagues(realm.game_id)
    if len(leagues) == 0:
        return []

    exalted_item = await currency_item_repository.get_exalted_item(realm.game_id)
    divine_item = await currency_item_repository.get_divine_item(realm.game_id)
    chaos_item = await currency_item_repository.get_chaos_item(realm.game_id)

    price_item_ids = [divine_item.item_id, chaos_item.item_id]
    price_rows = await price_log_repository.get_item_prices_by_league(
        price_item_ids,
        [league.league_id for league in leagues],
        realm.realm_id,
    )
    price_lookup = {(row.league_id, row.item_id): row.price for row in price_rows}

    return [
        GetResponse.from_model(
            league=league,
            exalted_item=exalted_item,
            divine_item=divine_item,
            chaos_item=chaos_item,
            price_lookup=price_lookup,
        )
        for league in leagues
    ]


class BaseCurrency(ApiModel):
    item_id: int
    api_id: str
    text: str
    icon_url: str | None = None
