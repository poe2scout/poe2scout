
from . import router
from fastapi import Depends
from services.apiService.dependancies import get_item_repository
from services.repositories import ItemRepository

@router.get("/{itemId}/history")
async def GetHistory(itemId: int, league: str, logCount: int, item_repository: ItemRepository = Depends(get_item_repository)):
    leagues = await item_repository.GetLeagues()
    leagueId = next((l.id for l in leagues if l.value == league), None)
    history = await item_repository.GetItemPriceHistory(itemId, leagueId, logCount)

    return history
