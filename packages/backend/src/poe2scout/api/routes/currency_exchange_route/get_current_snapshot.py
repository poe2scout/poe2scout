from decimal import Decimal
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Query

from poe2scout.api.dependancies import CXRepoDep, ItemRepoDep
from poe2scout.api.models import ApiModel
from poe2scout.db.repositories.currency_exchange_repository.get_current_snapshot import (
    GetCurrencyExchangeModel,
)

from . import router


class GetCurrentSnapshotResponse(ApiModel):
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

class GetCurrentSnapshotRequest(ApiModel):
    league_name: str

def get_current_snapshot_request(
    league_name: Annotated[str, Query(alias="LeagueName")],
) -> GetCurrentSnapshotRequest:
    return GetCurrentSnapshotRequest(league_name=league_name)

GetCurrentSnapshotRequestDep = Annotated[
    GetCurrentSnapshotRequest,
    Depends(get_current_snapshot_request),
]

@router.get("")
async def get_current_snapshot(
    request: GetCurrentSnapshotRequestDep,
    item_repository: ItemRepoDep,
    currency_exchange_repository: CXRepoDep,
) -> GetCurrentSnapshotResponse:
    league = await item_repository.get_league_by_value(request.league_name)

    if league is None:
        raise HTTPException(400, "Invalid league name")

    snapshot = await currency_exchange_repository.get_currency_exchange(league.id)

    if snapshot is None:
        raise HTTPException(404, "No data for given league.")

    return GetCurrentSnapshotResponse.from_model(snapshot)
