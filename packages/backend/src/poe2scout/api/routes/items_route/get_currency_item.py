from datetime import datetime
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query
from pydantic import BaseModel

from poe2scout.api.dependancies import ItemRepoDep
from poe2scout.api.dependancies import cache_response
from poe2scout.db.repositories.models import CurrencyItem, PriceLogEntry

from . import router

class GetCurrencyItemResponse(BaseModel):
    class _PriceLogEntry(BaseModel):
        price: float
        time: datetime
        quantity: int

        @classmethod
        def from_model(cls, price_log: PriceLogEntry) -> Self:
            return cls(
                price=price_log.price,
                time=price_log.time,
                quantity=price_log.quantity,
            )

    id: int
    itemId: int
    currencyCategoryId: int
    apiId: str
    text: str
    categoryApiId: str
    iconUrl: str | None
    itemMetadata: dict | None = None
    priceLogs: list[_PriceLogEntry | None]
    currentPrice: float | None = None

    @classmethod
    def from_model(
        cls, currency_item: CurrencyItem, price_logs: list[PriceLogEntry | None]
    ) -> Self:
        return cls(
            id=currency_item.id,
            itemId=currency_item.itemId,
            currencyCategoryId=currency_item.currencyCategoryId,
            apiId=currency_item.apiId,
            text=currency_item.text,
            categoryApiId=currency_item.categoryApiId,
            iconUrl=currency_item.iconUrl,
            itemMetadata=currency_item.itemMetadata,
            priceLogs=[
                cls._PriceLogEntry.from_model(price_log)
                if price_log is not None
                else None
                for price_log in price_logs
            ],
            currentPrice=next(
                (
                    price_log.price
                    for price_log in price_logs
                    if price_log is not None
                ),
                None,
            ),
        )

class GetItemCurrencyRequest(BaseModel):
    api_id: str
    league_name: str

def get_item_currency_request(
    api_id: Annotated[str, Path(alias="apiId")],
    league_name: Annotated[str, Query(alias="leagueName")]
)-> GetItemCurrencyRequest:
    return GetItemCurrencyRequest(
        api_id=api_id,
        league_name=league_name
    )

GetCurrencyItemRequestDep = Annotated[
    GetItemCurrencyRequest,
    Depends(get_item_currency_request),
]

@router.get("/Currency/{apiId}")
@cache_response(
    key=lambda kwargs: f"get_currency_item:{kwargs['api_id']}:{kwargs['league_name']}"
)
async def get_currency_item(
    request: GetCurrencyItemRequestDep,
    repo: ItemRepoDep
) -> GetCurrencyItemResponse:
    
    currency_item = await repo.GetCurrencyItem(request.api_id)
    if not currency_item:
        raise HTTPException(400, "Invalid currency item api ID")

    league = await repo.GetLeagueByValue(request.league_name)
    if not league:
        raise HTTPException(400, "Invalid league name")

    price_logs_by_item_id = await repo.GetItemPriceLogs(
        itemIds=[currency_item.itemId], 
        leagueId=league.id
    )

    return GetCurrencyItemResponse.from_model(
        currency_item, 
        price_logs_by_item_id.get(currency_item.itemId, [])
    )
