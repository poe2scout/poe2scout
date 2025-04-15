from services.apiService.dependancies import PaginationParams, get_pagination_params, get_item_repository
from fastapi import Depends
from services.repositories import ItemRepository
from pydantic import BaseModel
from services.repositories.item_repository.GetAllUniqueItems import UniqueItem
import math
from services.repositories.item_repository.GetItemPriceLogs import PriceLogEntry
from datetime import datetime
from typing import Optional
from services.repositories.item_repository.GetAllUniqueBaseItems import UniqueBaseItem
from enum import Enum
from . import router

class SortOptions(str, Enum):
    price = "price"
    item_name = "name"
    uniquePrice = "uniquePrice"
    negativePrice = "-price"
    negativeUniquePrice = "-uniquePrice"
    negativeName = "-name"

class PaginatedResponse(BaseModel):
    currentPage: int
    pages: int
    total: int


class UniqueBaseItemExtended(UniqueBaseItem):
    priceLogs: list[PriceLogEntry | None]
    currentPrice: Optional[float] = None
    averageUniquePrice: Optional[float] = None


class GetUniqueBaseItemsResponse(PaginatedResponse):
    items: list[UniqueBaseItemExtended]


@router.get("/uniqueBaseItems")
async def GetUniqueBaseItems(search: str = "", sortedBy: SortOptions = SortOptions.price, pagination: PaginationParams = Depends(get_pagination_params), repo: ItemRepository = Depends(get_item_repository)) -> GetUniqueBaseItemsResponse:
    
    uniqueBaseItems = await repo.GetAllUniqueBaseItems()
    if search:
        uniqueItems = [item for item in uniqueBaseItems if search.lower() in item.name.lower()]
    itemIds = [item.itemId for item in uniqueBaseItems]

    league = await repo.GetLeagueByValue(pagination.league)

    priceLogs = await repo.GetItemPriceLogs(itemIds, league.id)

    averageUniquePrice = await repo.GetAverageUniquePrice(itemIds, league.id)

    items = [UniqueBaseItemExtended(
        **item.model_dump(), priceLogs=priceLogs[item.itemId], averageUniquePrice=averageUniquePrice[item.itemId]) for item in uniqueBaseItems]

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

    items = [UniqueBaseItemExtended(
    **item.model_dump(exclude={'currentPrice'}), currentPrice=lastPrice[item.itemId]) for item in items]

    if sortedBy == SortOptions.price:
        items.sort(key=lambda item: item.currentPrice if item.currentPrice else 0, reverse=True)
    elif sortedBy == SortOptions.negativePrice:
        items.sort(key=lambda item: item.currentPrice if item.currentPrice else 0, reverse=False)
    elif sortedBy == SortOptions.item_name:
        items.sort(key=lambda item: item.name, reverse=True)
    elif sortedBy == SortOptions.negativeName:
        items.sort(key=lambda item: item.name, reverse=False)
    elif sortedBy == SortOptions.uniquePrice:
        items.sort(key=lambda item: item.averageUniquePrice if item.averageUniquePrice else 0, reverse=True)
    elif sortedBy == SortOptions.negativeUniquePrice:
        items.sort(key=lambda item: item.averageUniquePrice if item.averageUniquePrice else 0, reverse=False)


    items = items[startingIndex:endingIndex]
    return GetUniqueBaseItemsResponse(
        currentPage=pagination.page,
        pages=math.ceil(itemCount / pagination.perPage),
        total=itemCount,
        items=items
    )
