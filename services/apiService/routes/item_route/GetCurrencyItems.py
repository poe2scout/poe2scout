from services.apiService.dependancies import PaginationParams, get_pagination_params, get_item_repository, cache_response
from fastapi import Depends
from services.repositories import ItemRepository
from pydantic import BaseModel
import math
from services.repositories.item_repository.GetItemPriceLogs import PriceLogEntry
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from datetime import datetime
from typing import Optional

from . import router


class PaginatedResponse(BaseModel):
    currentPage: int
    pages: int
    total: int


class CurrencyItemExtended(CurrencyItem):
    priceLogs: list[PriceLogEntry | None]
    currentPrice: Optional[float] = None

class GetCurrencyItemsResponse(PaginatedResponse):
    items: list[CurrencyItemExtended]


@router.get("/currency/{category}")
@cache_response(key=lambda kwargs: f"GetCurrencyItems:{kwargs['category']}{kwargs['search']}page{kwargs['pagination'].page}perpage{kwargs['pagination'].perPage}{kwargs['pagination'].league}")
async def GetCurrencyItems(category: str, search: str = "", pagination: PaginationParams = Depends(get_pagination_params), repo: ItemRepository = Depends(get_item_repository)) -> GetCurrencyItemsResponse:

    currencyItems = await repo.GetCurrencyItemsByCategory(category, search)
    league = await repo.GetLeagueByValue(pagination.league)
    itemsInCurrentLeague = await repo.GetItemsInCurrentLeague(league.id)

    currencyItems = [currencyItem for currencyItem in currencyItems if currencyItem.itemId in itemsInCurrentLeague]
    itemIds = [item.itemId for item in currencyItems]
    
    priceLogs = await repo.GetItemPriceLogs(itemIds, league.id)

    items = [CurrencyItemExtended(
        **item.model_dump(), priceLogs=priceLogs[item.itemId]) for item in currencyItems]


    itemCount = len(items)
    lastPrice = dict.fromkeys(itemIds, 0)

    for item in items:
        for log in item.priceLogs:
            if log and hasattr(log, 'price'):
                lastPrice[item.itemId] = log.price
                break
           

    items.sort(
        key=lambda item: (
            lastPrice[item.itemId]
            if item.itemId in lastPrice
            else 0
        ),
        reverse=True
    )
    startingIndex = (pagination.page-1) * pagination.perPage
    endingIndex = startingIndex + pagination.perPage

    items = items[startingIndex:endingIndex]

    items = [CurrencyItemExtended(
        **item.model_dump(exclude={'currentPrice'}), currentPrice=lastPrice[item.itemId]) for item in items]

    return GetCurrencyItemsResponse(
        currentPage=pagination.page,
        pages=math.ceil(itemCount / pagination.perPage),
        total=itemCount,
        items=items
    )
