from services.apiService.dependancies import PaginationParams, get_pagination_params, get_item_repository
from fastapi import Depends, HTTPException
from services.repositories import ItemRepository
from pydantic import BaseModel
import math
from services.apiService.routes.item_route.GetCurrencyItems import CurrencyItemExtended
from . import router
from services.apiService.dependancies import cache_response



class GetCurrencyItemsResponse(BaseModel):
    item: CurrencyItemExtended


@router.get("/currencyById/{apiId}")
@cache_response(key=lambda kwargs: f"GetCurrencyItemsById:{kwargs['apiId']}")
async def GetCurrencyItemById(apiId: str, league: str, repo: ItemRepository = Depends(get_item_repository)) -> GetCurrencyItemsResponse:

    currencyItem = await repo.GetCurrencyItem(apiId)

    itemIds = [currencyItem.itemId]
    leagueInDb = await repo.GetLeagueByValue(league)
    if not leagueInDb:
        raise HTTPException(400, "Invalid league name")
    
    priceLogs = await repo.GetItemPriceLogs(itemIds, leagueInDb.id)

    items = [CurrencyItemExtended(
        **currencyItem.model_dump(), priceLogs=priceLogs[currencyItem.itemId])]


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

    item = CurrencyItemExtended(
        **item.model_dump(exclude={'currentPrice'}), currentPrice=lastPrice[item.itemId])

    return GetCurrencyItemsResponse(
        item=item
    )
