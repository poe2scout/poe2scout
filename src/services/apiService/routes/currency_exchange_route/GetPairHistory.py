from datetime import datetime, timezone
from typing import Optional
from services.repositories.currency_exchange_repository.GetPairHistory import (
    GetPairHistoryModel,
)
from . import router
from fastapi import HTTPException
from services.apiService.dependancies import CXRepoDep, ItemRepoDep


@router.get("/PairHistory")
async def GetPairHistory(
    league: str,
    currencyOneItemId: int,
    currencyTwoItemId: int,
    limit: int,
    item_repo: ItemRepoDep,
    cx_repo: CXRepoDep,
    endEpoch: Optional[int] = None,
) -> GetPairHistoryModel:
    leagueInDb = await item_repo.GetLeagueByValue(league)

    if not leagueInDb:
        raise HTTPException(400, "Invalid league name")

    getCurrencyExchangeResponse = await cx_repo.GetPairHistory(
        currencyOneItemId,
        currencyTwoItemId,
        leagueInDb.id,
        endEpoch if endEpoch else int(datetime.now(tz=timezone.utc).timestamp()),
        limit,
    )

    if not getCurrencyExchangeResponse:
        raise HTTPException(404, "No data for given league.")

    return getCurrencyExchangeResponse
