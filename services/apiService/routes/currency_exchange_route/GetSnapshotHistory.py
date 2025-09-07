from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from services.repositories.currency_exchange_repository.GetCurrentSnapshot import GetCurrencyExchangeModel
from services.repositories.currency_exchange_repository.GetCurrentSnapshotHistory import GetCurrencyExchangeHistoryModel
from . import router
from fastapi import HTTPException
from services.apiService.dependancies import CXRepoDep, ItemRepoDep

@router.get("/SnapshotHistory")
async def GetSnapshotHistory(league: str, limit: int, item_repo:  ItemRepoDep, cx_repo: CXRepoDep, endTime: Optional[int] = None) -> GetCurrencyExchangeHistoryModel:
    leagueInDb = await item_repo.GetLeagueByValue(league)

    if not leagueInDb:
        raise HTTPException(400, "Invalid league name")

    getCurrencyExchangeResponse = await cx_repo.GetCurrencyExchangeHistory(
        leagueInDb.id, 
        endTime if endTime else int(datetime.now(tz=timezone.utc).timestamp()),
        limit)

    if not getCurrencyExchangeResponse:
        raise HTTPException(404, "No data for given league.")
    
    return getCurrencyExchangeResponse
