from typing import Self

from fastapi import APIRouter, HTTPException
from poe2scout.api.dependancies import ItemRepoDep
from pydantic import BaseModel

router = APIRouter(prefix="/Leagues")

class GetLeaguesResponse(BaseModel):
    value: str
    divine_price: float
    chaos_divine_price: float

    @classmethod
    def from_model(
        cls, 
        value: str, 
        divine_price: float, 
        chaos_divine_price: float
    ) -> Self:
        return cls(
            value=value,
            divine_price=divine_price,
            chaos_divine_price=chaos_divine_price
        )

@router.get("")
async def get_leagues(
    item_repository: ItemRepoDep,
) -> list[GetLeaguesResponse]:
    leagues = await item_repository.GetAllLeagues()

    divine_item = await item_repository.GetCurrencyItem("divine")
    if divine_item is None:
        raise HTTPException(500)
    
    chaos_item = await item_repository.GetCurrencyItem("chaos")
    if chaos_item is None:
        raise HTTPException(500)

    responses = []
    for league in leagues:
        divine_price = await item_repository.GetItemPrice(divine_item.itemId, league.id)
        chaos_price = await item_repository.GetItemPrice(chaos_item.itemId, league.id)

        responses.append(
            LeagueResponse.from_model(
                value=league.value,
                divine_price=divine_price if divine_price is not None else 50,
                chaos_divine_price=divine_price / chaos_price
                if chaos_price is not None
                else 50,
            )
        )

    return responses
