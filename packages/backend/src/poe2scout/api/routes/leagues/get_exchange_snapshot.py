from decimal import Decimal
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path

from poe2scout.api.api_model import ApiModel
from poe2scout.api.dependancies import LeagueContextDep
from poe2scout.db.repositories import (
    currency_exchange_repository,
)
from poe2scout.db.repositories.currency_exchange_repository.get_current_snapshot import (
    GetCurrencyExchangeModel,
)

from . import router

class GetExchangeSnapshotResponse(ApiModel):
    epoch: int
    volume: Decimal
    market_cap: Decimal
    base_currency_api_id: str
    base_currency_text: str

    @classmethod
    def from_model(
        cls,
        model: GetCurrencyExchangeModel,
        base_currency_api_id: str,
        base_currency_text: str,
    ) -> Self:
        return cls(
            epoch=model.epoch,
            volume=model.volume,
            market_cap=model.market_cap,
            base_currency_api_id=base_currency_api_id,
            base_currency_text=base_currency_text,
        )

class GetExchangeSnapshotRequest(ApiModel):
    league_name: str
    realm: str

def get_exchange_snapshot_request(
    league_name: Annotated[str, Path(alias="LeagueName")],
    realm: Annotated[str, Path(alias="Realm")],
) -> GetExchangeSnapshotRequest:
    return GetExchangeSnapshotRequest(
        league_name=league_name,
        realm=realm
    )

GetExchangeSnapshotRequestDep = Annotated[
    GetExchangeSnapshotRequest,
    Depends(get_exchange_snapshot_request),
]

@router.get("/{LeagueName}/ExchangeSnapshot")
async def get_exchange_snapshot(
    request: GetExchangeSnapshotRequestDep,
    context: LeagueContextDep,
) -> GetExchangeSnapshotResponse:
    realm = context.realm
    league = context.league

    snapshot = await currency_exchange_repository.get_currency_exchange(
        league.league_id, 
        realm.realm_id
    )

    if snapshot is None:
        raise HTTPException(404, "No data for given league.")

    return GetExchangeSnapshotResponse.from_model(
        snapshot,
        base_currency_api_id=league.base_currency_api_id,
        base_currency_text=league.base_currency_text,
    )
