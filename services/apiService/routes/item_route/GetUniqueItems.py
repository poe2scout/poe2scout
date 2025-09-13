from services.apiService.dependancies import EconomyCacheDep, PaginationParams, get_pagination_params, get_item_repository
from fastapi import Depends, HTTPException
from services.repositories import ItemRepository
from pydantic import BaseModel
from services.repositories.item_repository.GetAllUniqueItems import UniqueItem
import math
from datetime import datetime
from typing import Optional
from services.apiService.dependancies import cache_response
from services.repositories.models import UniqueItemExtended
from . import router


class PaginatedResponse(BaseModel):
    currentPage: int
    pages: int
    total: int



class GetUniqueItemsResponse(PaginatedResponse):
    items: list[UniqueItemExtended]


@router.get("/unique/{category}")
async def GetUniqueItems(category: str, econCache: EconomyCacheDep, referenceCurrency: str = "exalted", search: str = "", pagination: PaginationParams = Depends(get_pagination_params), repo: ItemRepository = Depends(get_item_repository)) -> GetUniqueItemsResponse:
    if referenceCurrency not in ["exalted", "chaos"]:
        raise HTTPException(400, "reference currency must be exalted or chaos")

    leagueInDb = await repo.GetLeagueByValue(pagination.league)
    if not leagueInDb:
        raise HTTPException(400, "Invalid league name")
    
    items = await econCache.GetUniquePage(leagueInDb.id, category, search, referenceCurrency)
    itemCount = len(items)

    startingIndex = (pagination.page-1) * pagination.perPage
    endingIndex = startingIndex + pagination.perPage

    items = items[startingIndex:endingIndex]

    return GetUniqueItemsResponse(
        currentPage=pagination.page,
        pages=math.ceil(itemCount / pagination.perPage),
        total=itemCount,
        items=items
    )
