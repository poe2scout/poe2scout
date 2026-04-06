from decimal import Decimal
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path

from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories import currency_exchange_repository, league_repository, realm_repository
from poe2scout.db.repositories.currency_exchange_repository.get_current_snapshot import (
    GetCurrencyExchangeModel,
)

from . import router

class GetExchangeSnapshotResponse(ApiModel):
    epoch: int
    volume: Decimal
    market_cap: Decimal

    @classmethod
    def from_model(cls, model: GetCurrencyExchangeModel) -> Self:
        return cls(
            epoch=model.epoch,
            volume=model.volume,
            market_cap=model.market_cap,
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
) -> GetExchangeSnapshotResponse:
    realm = await realm_repository.get_realm(request.realm)

    if realm is None:
        raise HTTPException(400, "Invalid realm")

    league = await league_repository.get_league_by_value(request.league_name, realm.game_id)

    if league is None:
        raise HTTPException(400, "Invalid league name")

    snapshot = await currency_exchange_repository.get_currency_exchange(league.league_id, realm.realm_id)

    if snapshot is None:
        raise HTTPException(404, "No data for given league.")

    return GetExchangeSnapshotResponse.from_model(snapshot)
