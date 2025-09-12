
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel

from services.repositories.models import PriceLogEntry

from . import router
from fastapi import Depends, HTTPException
from services.apiService.dependancies import get_item_repository
from services.repositories import ItemRepository

class PricePoint(BaseModel):
    price: float
    time: datetime
    quantity: int

@router.get("/{itemId}/history")
async def GetHistory(itemId: int, league: str, logCount: int, endTime: datetime = datetime.now(tz=timezone.utc), referenceCurrency: str = 'exalted', item_repository: ItemRepository = Depends(get_item_repository)):
    if logCount % 4 != 0:
        return HTTPException(400, "logCount must be a multiple of 4")
    
    leagues = await item_repository.GetAllLeagues()
    leagueId = next((l.id for l in leagues if l.value == league), None)

    isACurrency = await item_repository.IsItemACurrency(itemId)

    if isACurrency:
        logFrequency = 1
    else:
        logFrequency = 6
    
    history = await item_repository.GetItemPriceHistory(itemId, leagueId, logCount, logFrequency, endTime)

    if referenceCurrency != 'exalted':
        referenceCurrencyItem = await item_repository.GetCurrencyItem(referenceCurrency)
        referenceCurrencyHistory = await item_repository.GetItemPriceHistory(referenceCurrencyItem.itemId, leagueId, logCount, logFrequency, endTime)

        referenceCurrencyHistoryLookup = {log.time: log for log in referenceCurrencyHistory.price_history}

        logs = history.price_history
        newLogs = []
        lastReferencePrice = 0
        for log in logs:
            if log == None:
                continue
            
            currentReferenceLog = referenceCurrencyHistoryLookup.get(log.time)
            if currentReferenceLog != None:
                lastReferencePrice = currentReferenceLog.price 

            if lastReferencePrice == 0:
                continue
            newLogEntry = PriceLogEntry(price=log.price / lastReferencePrice, time = log.time, quantity = log.quantity)
            newLogs.append(newLogEntry)
        history.price_history = newLogs

    return history