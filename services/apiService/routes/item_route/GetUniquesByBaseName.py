from services.apiService.dependancies import PaginationParams, get_pagination_params, get_item_repository
from fastapi import Depends
from services.repositories import ItemRepository
from pydantic import BaseModel
from services.repositories.item_repository.GetAllUniqueItems import UniqueItem
import math
from services.repositories.item_repository.GetItemPriceLogs import PriceLogEntry
from datetime import datetime
from typing import Optional
from services.apiService.routes.item_route.GetUniqueItems import UniqueItemExtended
from services.apiService.dependancies import cache_response
from . import router


class PaginatedResponse(BaseModel):
    currentPage: int
    pages: int
    total: int


class GetUniquesByBaseNameResponse(BaseModel):
    items: list[UniqueItemExtended]



@router.get("/uniquesByBaseName/{baseName}")
@cache_response(key=lambda kwargs: f"GetUniquesByBaseName:{kwargs['baseName']}{kwargs['league']}")
async def GetUniquesByBaseName(baseName: str, league: str, repo: ItemRepository = Depends(get_item_repository)) -> GetUniquesByBaseNameResponse:

    uniqueItems = await repo.GetUniqueItemsByBaseName(baseName)
    leagueInDb = await repo.GetLeagueByValue(league)

    itemsInCurrentLeague = await repo.GetItemsInCurrentLeague(leagueInDb.id)

    uniqueItems = [uniqueItem for uniqueItem in uniqueItems if uniqueItem.itemId in itemsInCurrentLeague]
    itemIds = [item.itemId for item in uniqueItems]

    priceLogs = await repo.GetItemPriceLogs(itemIds, leagueInDb.id)

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


    items = [UniqueItemExtended(
        **item.model_dump(exclude={'currentPrice'}), currentPrice=lastPrice[item.itemId]) for item in items]

    return GetUniquesByBaseNameResponse(
        items=items
    )
