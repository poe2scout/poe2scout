from services.repositories.models import PriceLogEntry
from . import router
from fastapi import Depends, HTTPException
from services.apiService.dependancies import get_item_repository
from services.repositories import ItemRepository
from services.repositories.item_repository.GetAllUniqueItems import UniqueItem
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from typing import Optional, Union, List
from asyncio import gather
from urllib.parse import quote
from pydantic import BaseModel
from services.repositories.item_repository.GetLeagues import League
from services.apiService.dependancies import cache_response
from cachetools import TTLCache
from cachetools.keys import hashkey

class UniqueItemResponse(BaseModel):
    itemId: int
    name: str
    type: str
    categoryApiId: str
    priceLogs: List[PriceLogEntry | None]
    currentPrice: float
    iconUrl: Optional[str]

class CurrencyItemResponse(BaseModel):
    itemId: int
    apiId: str
    text: str
    categoryApiId: str
    priceLogs: List[PriceLogEntry | None]
    currentPrice: float
    iconUrl: Optional[str]

items_cache = TTLCache(maxsize=1, ttl=60*15)

@router.get("")
async def GetAllItems(league: str, item_repository: ItemRepository = Depends(get_item_repository)) -> list[UniqueItemResponse | CurrencyItemResponse]:

    cache_key = hashkey(league)
    
    if cache_key in items_cache:
        return items_cache[cache_key]

    unique_items, currency_items, leagues = await gather(
        item_repository.GetAllUniqueItems(),
        item_repository.GetAllCurrencyItems(),
        item_repository.GetAllLeagues()
    )
    
    items = unique_items + currency_items
    item_ids = [item.itemId for item in items]
    
    league_id = next((l.id for l in leagues if l.value == league), None)
    if league_id is None:
        raise HTTPException(status_code=404, detail="League not found")
        
    price_logs = await item_repository.GetItemPriceLogs(item_ids, league_id)
    
    last_prices = {}
    for item_id, logs in price_logs.items():
        last_prices[item_id] = next((log.price for log in logs if log and hasattr(log, 'price')), 0)
    
    responses = []
    responses.extend([
        UniqueItemResponse(
            **item.model_dump(),
            priceLogs=price_logs[item.itemId],
            currentPrice=last_prices[item.itemId]
        ) for item in unique_items
    ])
    responses.extend([
        CurrencyItemResponse(
            **item.model_dump(),
            priceLogs=price_logs[item.itemId],
            currentPrice=last_prices[item.itemId]
        ) for item in currency_items
    ])
    
    items_cache[cache_key] = responses
    return responses


