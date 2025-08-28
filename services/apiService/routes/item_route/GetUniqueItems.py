from services.apiService.dependancies import PaginationParams, get_pagination_params, get_item_repository
from fastapi import Depends
from services.repositories import ItemRepository
from pydantic import BaseModel
from services.repositories.item_repository.GetAllUniqueItems import UniqueItem
import math
from services.repositories.item_repository.GetItemPriceLogs import PriceLogEntry
from datetime import datetime
from typing import Optional
from services.apiService.dependancies import cache_response
from . import router


class PaginatedResponse(BaseModel):
    currentPage: int
    pages: int
    total: int


class UniqueItemExtended(UniqueItem):
    priceLogs: list[PriceLogEntry | None]
    currentPrice: Optional[float] = None
    
class GetUniqueItemsResponse(PaginatedResponse):
    items: list[UniqueItemExtended]


@router.get("/unique/{category}")
@cache_response(key=lambda kwargs: f"GetUniqueItems:{kwargs['category']}{kwargs['search']}page{kwargs['pagination'].page}perpage{kwargs['pagination'].perPage}{kwargs['pagination'].league}")
async def GetUniqueItems(category: str, search: str = "", pagination: PaginationParams = Depends(get_pagination_params), repo: ItemRepository = Depends(get_item_repository)) -> GetUniqueItemsResponse:

    uniqueItems = await repo.GetUniqueItemsByCategory(category)
    league = await repo.GetLeagueByValue(pagination.league)

    if search:
        uniqueItems = [item for item in uniqueItems if search.lower() in item.name.lower()]
    itemsInCurrentLeague = await repo.GetItemsInCurrentLeague(league.id)

    itemIds = [item.itemId for item in uniqueItems if item.itemId in itemsInCurrentLeague]


    priceLogs = await repo.GetItemPriceLogs(itemIds, league.id)

    items = [UniqueItemExtended(
        **item.model_dump(), priceLogs=priceLogs[item.itemId]) for item in uniqueItems]


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

    items = [UniqueItemExtended(
        **item.model_dump(exclude={'currentPrice'}), currentPrice=lastPrice[item.itemId]) for item in items]

    return GetUniqueItemsResponse(
        currentPage=pagination.page,
        pages=math.ceil(itemCount / pagination.perPage),
        total=itemCount,
        items=items
    )
