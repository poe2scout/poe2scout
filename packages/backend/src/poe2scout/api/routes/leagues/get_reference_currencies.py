from typing import Annotated, Self

from fastapi import Depends, Path

from poe2scout.api.dependancies import LeagueContextDep
from poe2scout.api.routes.leagues.get import BaseCurrency
from poe2scout.db.repositories.game_repository.get_bridge_currencies import BridgeCurrency
from poe2scout.db.repositories.league_repository.get_leagues import League
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories import (
    game_repository,
    price_log_repository,
)

from . import router


class GetReferenceCurrenciesRequest(ApiModel):
    realm: str
    league_name: str


def get_reference_currencies_request(
    realm: Annotated[str, Path(alias="Realm")],
    league_name: Annotated[str, Path(alias="LeagueName")],
) -> GetReferenceCurrenciesRequest:
    return GetReferenceCurrenciesRequest(realm=realm, league_name=league_name)


GetReferenceCurrenciesRequestDep = Annotated[
    GetReferenceCurrenciesRequest,
    Depends(get_reference_currencies_request),
]

class ReferenceCurrency(ApiModel):
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



@router.get("/{LeagueName}/ReferenceCurrencies")
async def get_reference_currencies(
    request: GetReferenceCurrenciesRequestDep,
    context: LeagueContextDep,
) -> list[ReferenceCurrency]:
    realm = context.realm
    league = context.league

    bridge_currencies = await game_repository.get_bridge_currencies(realm.game_id)
    base_currencies = get_base_currencies(league, bridge_currencies)
    bridge_item_ids = [
        currency.item_id
        for currency in base_currencies
        if currency.item_id != league.base_currency_item_id
    ]
    price_rows = await price_log_repository.get_item_prices_by_league(
        bridge_item_ids,
        [league.league_id],
        realm.realm_id,
    )
    price_lookup = {(row.league_id, row.item_id): row.price for row in price_rows}

    return [
        ReferenceCurrency.from_model(currency, relative_price=1)
        if currency.item_id == league.base_currency_item_id
        else ReferenceCurrency.from_model(
            currency,
            relative_price=price_lookup.get((league.league_id, currency.item_id), 0),
        )
        for currency in base_currencies
    ]


def get_base_currencies(
    league: League,
    bridge_currencies: list[BridgeCurrency],
) -> list[BaseCurrency]:
    mapped_bridge_currencies = [
        BaseCurrency(
            item_id=currency.item_id,
            api_id=currency.api_id,
            text=currency.text,
            icon_url=currency.icon_url,
        )
        for currency in bridge_currencies
    ]

    return [
        BaseCurrency(
            item_id=league.base_currency_item_id,
            api_id=league.base_currency_api_id,
            text=league.base_currency_text,
            icon_url=league.base_currency_icon_url,
        ),
        *mapped_bridge_currencies,
    ]
