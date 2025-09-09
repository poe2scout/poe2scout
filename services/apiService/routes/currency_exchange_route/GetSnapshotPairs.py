from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel
from services.repositories.currency_exchange_repository.GetCurrentSnapshot import GetCurrencyExchangeModel
from services.repositories.currency_exchange_repository.GetCurrentSnapshotHistory import GetCurrencyExchangeHistoryModel
from services.repositories.currency_exchange_repository.GetCurrentSnapshotPairs import GetCurrentSnapshotPairModel, GetCurrentSnapshotPairs
from . import router
from fastapi import HTTPException
from services.apiService.dependancies import CXRepoDep, ItemRepoDep

@router.get("/SnapshotPairs")
async def GetSnapshotPairs(league: str, item_repo:  ItemRepoDep, cx_repo: CXRepoDep) -> List[GetCurrentSnapshotPairModel]:
    leagueInDb = await item_repo.GetLeagueByValue(league)
    if not leagueInDb:
        raise HTTPException(400, "Invalid league name")

    getCurrencyExchangeResponse = await cx_repo.GetCurrentSnapshotPairs(leagueInDb.id)
    
    return getCurrencyExchangeResponse



