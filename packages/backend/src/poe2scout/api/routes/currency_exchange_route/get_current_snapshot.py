from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel

from poe2scout.db.repositories.currency_exchange_repository.GetCurrentSnapshot import (
    GetCurrencyExchangeModel,
)
from . import router
from fastapi import HTTPException, Query
from poe2scout.api.dependancies import CXRepoDep, ItemRepoDep

class GetCurrentSnapshotResponse(BaseModel):
    epoch: int
    volume: Decimal
    market_cap: Decimal

    @classmethod
    def from_model(cls, model: GetCurrencyExchangeModel) -> Self:
        return cls(
            epoch=model.Epoch,
            volume=model.Volume,
            market_cap=model.MarketCap
        )


class GetCurrentSnapshotRequest(BaseModel):
    league_name: str

def get_current_snapshot_request(
    league_name: Annotated[str, Query(alias="leagueName")]
) -> GetCurrentSnapshotRequest:
    return GetCurrentSnapshotRequest(
        league_name=league_name
    )

GetCurrentSnapshotRequestDep = Annotated[
    GetCurrentSnapshotRequest,
    get_current_snapshot_request
]

@router.get("")
async def get_current_snapshot(
    request: GetCurrentSnapshotRequestDep, 
    item_repository: ItemRepoDep, 
    currency_exchange_repository: CXRepoDep
) -> GetCurrentSnapshotResponse:
    league = await item_repository.GetLeagueByValue(request.league_name)

    if not league:
        raise HTTPException(400, "Invalid league name")

    snapshot = await currency_exchange_repository.GetCurrencyExchange(
        league.id
    )

    if not snapshot:
        raise HTTPException(404, "No data for given league.")

    return GetCurrentSnapshotResponse.from_model(
        model=snapshot
    )
