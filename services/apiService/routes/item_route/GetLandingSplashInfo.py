
from . import router
from fastapi import Depends
from services.apiService.dependancies import get_item_repository
from services.repositories import ItemRepository
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from services.apiService.routes.item_route.GetCurrencyItems import CurrencyItemExtended
from pydantic import BaseModel
importantApiIds = ["mirror","divine","exalted","annul"]
defaultLeagueId = 1

class LandingSplashInfoResponse(BaseModel):
    items: list[CurrencyItemExtended]

@router.get("/landingSplashInfo")
async def GetLandingSplashInfo(item_repository: ItemRepository = Depends(get_item_repository)) -> LandingSplashInfoResponse:

    items = await item_repository.GetCurrencyItems(importantApiIds)

    itemIds = [item.itemId for item in items]

    priceLogs = await item_repository.GetItemPriceLogs(itemIds, defaultLeagueId)

    items = [CurrencyItemExtended(
        **item.model_dump(), priceLogs=priceLogs[item.itemId]) for item in items]

    lastPrice = dict.fromkeys(itemIds, 0)

    for item in items:
        for log in item.priceLogs:
            if log and hasattr(log, 'price'):
                lastPrice[item.itemId] = log.price
                break
           

    items.sort(
        key=lambda item: (
            int(lastPrice[item.itemId])
            if item.itemId in lastPrice
            else 0
        ),
        reverse=True
    )

    return LandingSplashInfoResponse(items=items)
