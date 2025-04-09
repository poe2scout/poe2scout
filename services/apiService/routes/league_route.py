from fastapi import APIRouter, Depends
from services.apiService.dependancies import get_item_repository
from services.repositories import ItemRepository
from pydantic import BaseModel

router = APIRouter(prefix="/leagues")

class LeagueResponse(BaseModel):
    value: str
    divinePrice: float

@router.get("")
async def GetLeagues(repo: ItemRepository = Depends(get_item_repository)) -> list[LeagueResponse]:
    leagues = await repo.GetLeagues()
    divine_item = await repo.GetCurrencyItem("divine")
    
    responses = []
    for league in leagues:
        divine_price = await repo.GetItemPrice(divine_item.itemId, league.id)
        responses.append(LeagueResponse(
            value=league.value,
            divinePrice=divine_price if divine_price is not None else 50
        ))
    
    return responses 