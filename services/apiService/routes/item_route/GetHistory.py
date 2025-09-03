
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from services.repositories.item_repository.GetItemPriceHistory import PriceLogEntry
from . import router
from fastapi import Depends, HTTPException
from services.apiService.dependancies import get_item_repository
from services.repositories import ItemRepository

class PricePoint(BaseModel):
    price: float
    time: datetime
    quantity: int

@router.get("/{itemId}/history")
async def GetHistory(itemId: int, league: str, logCount: int, referenceCurrency: str = 'exalted', item_repository: ItemRepository = Depends(get_item_repository)):
    if logCount % 4 != 0:
        return HTTPException(400, "logCount must be a multiple of 4")
    
    leagues = await item_repository.GetAllLeagues()
    leagueId = next((l.id for l in leagues if l.value == league), None)

    isACurrency = await item_repository.IsItemACurrency(itemId)

    if isACurrency and logCount < 14*4:
        logFrequency = 1
        actualLogCount = logCount * 6
    else:
        logFrequency = 6
        actualLogCount = logCount

    history = await item_repository.GetItemPriceHistory(itemId, leagueId, actualLogCount, logFrequency)
    newHistory: List[Optional[PricePoint]] = []

    if referenceCurrency != 'exalted':
        referenceCurrencyItem = await item_repository.GetCurrencyItem(referenceCurrency)
        referenceCurrencyHistory = await item_repository.GetItemPriceHistory(referenceCurrencyItem.itemId, leagueId, actualLogCount, logFrequency)

        logs = history['price_history']
        newLogs = []
        lastReferencePrice = 0
        for i, log in enumerate(logs):
            if log == None:
                newLogs.append(None)
                continue
            
            currentReferenceLog = referenceCurrencyHistory['price_history'][i]
            if currentReferenceLog != None:
                lastReferencePrice = currentReferenceLog.price 

            if lastReferencePrice == 0:
                newLogs.append(None)
                continue
            newLogEntry = PriceLogEntry(price=log.price / lastReferencePrice, time = log.time, quantity = log.quantity)
            newLogs.append(newLogEntry)
        history['price_history'] = newLogs

    logs = history['price_history']
    if logCount >= (14*4):
        for i in range(logCount//4):
            found = 0
            price = 0.0
            time = None
            quantity = 0
            for j in range(4):
                currentLog = logs[i*4+j]
                if currentLog != None:
                    found += 1
                    price += currentLog.price
                    time = currentLog.time 
                    quantity += currentLog.quantity
            if time != None:
                newHistory.append(PricePoint(price=price/found, time=time, quantity=quantity))
            else:
                newHistory.append(None)
        return {'price_history': newHistory}
    else:
        return history