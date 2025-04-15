from . import router
from fastapi import Depends
from services.apiService.dependancies import get_item_repository
from services.repositories import ItemRepository
from services.repositories.item_repository.GetAllUniqueItems import UniqueItem
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from services.repositories.item_repository.GetItemPriceLogs import PriceLogEntry
from typing import Optional, Union, List
from asyncio import gather
from urllib.parse import quote
from pydantic import BaseModel
from services.repositories.item_repository.GetLeagues import League

class UniqueItemResponse(BaseModel):
    name: str
    type: str
    categoryApiId: str
    priceLogs: List[PriceLogEntry | None]
    currentPrice: float

class CurrencyItemResponse(BaseModel):
    apiId: str
    text: str
    categoryApiId: str
    priceLogs: List[PriceLogEntry | None]
    currentPrice: float


@router.get("")
async def GetAllItems(league: str, item_repository: ItemRepository = Depends(get_item_repository)) -> list[UniqueItemResponse | CurrencyItemResponse]:
    unique_items, currency_items, leagues = await gather(
        item_repository.GetAllUniqueItems(),
        item_repository.GetAllCurrencyItems(),
        item_repository.GetLeagues()
    )
    
    items = unique_items + currency_items
    item_ids = [item.itemId for item in items]
    
    league_id = next((l.id for l in leagues if l.value == league))
    
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
    
    return responses

