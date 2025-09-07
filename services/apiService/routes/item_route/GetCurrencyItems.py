from services.apiService.dependancies import EconomyCacheDep, PaginationParams, get_pagination_params, get_item_repository, cache_response
from fastapi import Depends, HTTPException
from services.repositories import ItemRepository
from pydantic import BaseModel
import math
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from datetime import datetime
from typing import List, Optional

from services.repositories.models import CurrencyItemExtended

from . import router

class PaginatedResponse(BaseModel):
    currentPage: int
    pages: int
    total: int

class GetCurrencyItemsResponse(PaginatedResponse):
    items: list[CurrencyItemExtended]

#LeagueXCategory

@router.get("/currency/{category}")
async def GetCurrencyItems(category: str, econCache: EconomyCacheDep, search: str = "",  pagination: PaginationParams = Depends(get_pagination_params), repo: ItemRepository = Depends(get_item_repository)) -> GetCurrencyItemsResponse:
    leagueInDb = await repo.GetLeagueByValue(pagination.league)

    if not leagueInDb:
        raise HTTPException(400, "Invalid league name")

    items = await econCache.GetCurrencyPage(leagueInDb.id, category, search)
    itemCount = len(items)

    startingIndex = (pagination.page-1) * pagination.perPage
    endingIndex = startingIndex + pagination.perPage

    items = items[startingIndex:endingIndex]

    return GetCurrencyItemsResponse(
        currentPage=pagination.page,
        pages=math.ceil(itemCount / pagination.perPage),
        total=itemCount,
        items=items
    )
