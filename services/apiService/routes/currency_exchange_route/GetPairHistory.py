from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from services.repositories.currency_exchange_repository.GetCurrentSnapshot import GetCurrencyExchangeModel
from services.repositories.currency_exchange_repository.GetCurrentSnapshotHistory import GetCurrencyExchangeHistoryModel
from services.repositories.currency_exchange_repository.GetPairHistory import GetPairHistoryModel
from . import router
from fastapi import HTTPException
from services.apiService.dependancies import CXRepoDep, ItemRepoDep

@router.get("/PairHistory")
async def GetPairHistory(league: str, currencyOneApiId: str, currencyTwoApiId: str, limit: int, item_repo:  ItemRepoDep, cx_repo: CXRepoDep, endTime: Optional[int] = None) -> GetPairHistoryModel:
    leagueInDb = await item_repo.GetLeagueByValue(league)

    if not leagueInDb:
        raise HTTPException(400, "Invalid league name")

    getCurrencyExchangeResponse = await cx_repo.GetPairHistory(
        currencyOneApiId,
        currencyTwoApiId,
        leagueInDb.id, 
        endTime if endTime else int(datetime.now(tz=timezone.utc).timestamp()),
        limit)

    if not getCurrencyExchangeResponse:
        raise HTTPException(404, "No data for given league.")
    
    return getCurrencyExchangeResponse
