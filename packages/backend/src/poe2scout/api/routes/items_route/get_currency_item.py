from datetime import datetime
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query

from poe2scout.api.dependancies import ItemRepoDep, cache_response
from poe2scout.api.models import ApiModel
from poe2scout.db.repositories.models import CurrencyItem, PriceLogEntry

from . import router


class GetCurrencyItemResponse(ApiModel):
    class _PriceLogEntry(ApiModel):
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
    item_id: int
    currency_category_id: int
    api_id: str
    text: str
    category_api_id: str
    icon_url: str | None
    item_metadata: dict | None = None
    price_logs: list[_PriceLogEntry | None]
    current_price: float | None = None

    @classmethod
    def from_model(
        cls,
        currency_item: CurrencyItem,
        price_logs: list[PriceLogEntry | None],
    ) -> Self:
        return cls(
            id=currency_item.id,
            item_id=currency_item.itemId,
            currency_category_id=currency_item.currencyCategoryId,
            api_id=currency_item.apiId,
            text=currency_item.text,
            category_api_id=currency_item.categoryApiId,
            icon_url=currency_item.iconUrl,
            item_metadata=currency_item.itemMetadata,
            price_logs=[
                cls._PriceLogEntry.from_model(price_log)
                if price_log is not None
                else None
                for price_log in price_logs
            ],
            current_price=next(
                (price_log.price for price_log in price_logs if price_log is not None),
                None,
            ),
        )


class GetItemCurrencyRequest(ApiModel):
    api_id: str
    league_name: str


def get_item_currency_request(
    api_id: Annotated[str, Path(alias="ApiId")],
    league_name: Annotated[str, Query(alias="LeagueName")],
) -> GetItemCurrencyRequest:
    return GetItemCurrencyRequest(
        api_id=api_id,
        league_name=league_name,
    )


GetCurrencyItemRequestDep = Annotated[
    GetItemCurrencyRequest,
    Depends(get_item_currency_request),
]


@router.get("/Currency/{ApiId}")
@cache_response(
    key=lambda params: (
        f"get_currency_item:{params['request'].api_id}:{params['request'].league_name}"
    )
)
async def get_currency_item(
    request: GetCurrencyItemRequestDep,
    repo: ItemRepoDep,
) -> GetCurrencyItemResponse:
    currency_item = await repo.GetCurrencyItem(request.api_id)
    if currency_item is None:
        raise HTTPException(400, "Invalid currency item api ID")

    league = await repo.GetLeagueByValue(request.league_name)
    if league is None:
        raise HTTPException(400, "Invalid league name")

    price_logs_by_item_id = await repo.GetItemPriceLogs(
        itemIds=[currency_item.itemId],
        leagueId=league.id,
    )

    return GetCurrencyItemResponse.from_model(
        currency_item,
        price_logs_by_item_id.get(currency_item.itemId, []),
    )
