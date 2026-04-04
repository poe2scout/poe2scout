
from typing import Self

from fastapi import HTTPException
from poe2scout.api.dependancies import ItemRepoDep
from poe2scout.api.api_model import ApiModel
from . import router

class GetResponse(ApiModel):
    value: str
    divine_price: float
    chaos_divine_price: float

    @classmethod
    def from_model(
        cls,
        value: str,
        divine_price: float,
        chaos_divine_price: float,
    ) -> Self:
        return cls(
            value=value,
            divine_price=divine_price,
            chaos_divine_price=chaos_divine_price,
        )


@router.get("")
async def get(
    item_repository: ItemRepoDep,
) -> list[GetResponse]:
    leagues = await item_repository.get_all_leagues()

    divine_item = await item_repository.get_currency_item("divine")
    if divine_item is None:
        raise HTTPException(500)

    chaos_item = await item_repository.get_currency_item("chaos")
    if chaos_item is None:
        raise HTTPException(500)

    responses: list[GetResponse] = []
    for league in leagues:
        divine_price = await item_repository.get_item_price(divine_item.item_id, league.id)
        chaos_price = await item_repository.get_item_price(chaos_item.item_id, league.id)

        responses.append(
            GetResponse.from_model(
                value=league.value,
                divine_price=divine_price if divine_price is not None else 50,
                chaos_divine_price=divine_price / chaos_price
                if chaos_price is not None
                else 50,
            )
        )

    return responses
