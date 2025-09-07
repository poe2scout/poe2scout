from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from services.repositories.currency_exchange_repository.GetCurrencyExchange import GetCurrencyExchangeModel
from services.repositories.currency_exchange_repository.GetCurrencyExchangeHistory import GetCurrencyExchangeHistoryModel
from . import router
from fastapi import HTTPException
from services.apiService.dependancies import CXRepoDep, ItemRepoDep

@router.get("/history")
async def GetHistory(league: str, limit: int, item_repo:  ItemRepoDep, cx_repo: CXRepoDep, endTime: Optional[int] = None) -> GetCurrencyExchangeHistoryModel:
    leagueId = (await item_repo.GetLeagueByValue(league)).id

    getCurrencyExchangeResponse = await cx_repo.GetCurrencyExchangeHistory(
        leagueId, 
        endTime if endTime else int(datetime.now(tz=timezone.utc).timestamp()),
        limit)

    if not getCurrencyExchangeResponse:
        raise HTTPException(404, "No data for given league.")
    
    return getCurrencyExchangeResponse
