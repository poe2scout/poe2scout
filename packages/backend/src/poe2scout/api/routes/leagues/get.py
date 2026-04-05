
from typing import Self

from poe2scout.api.dependancies import CurrencyItemRepoDep, LeagueRepoDep, PriceLogRepoDep
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
    league_repository: LeagueRepoDep,
    currency_item_repository: CurrencyItemRepoDep,
    price_log_repository: PriceLogRepoDep
) -> list[GetResponse]:
    leagues = await league_repository.get_all_leagues()

    divine_item = await currency_item_repository.get_divine_item()

    chaos_item = await currency_item_repository.get_chaos_item()

    responses: list[GetResponse] = []
    for league in leagues:
        divine_price = await price_log_repository.get_item_price(
            divine_item.item_id, 
            league.league_id
        )
        chaos_price = await price_log_repository.get_item_price(
            chaos_item.item_id, 
            league.league_id
        )

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
