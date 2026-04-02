import math
from datetime import datetime
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query

from poe2scout.api.dependancies import EconomyCacheDep, ItemRepoDep, PaginationParamDep
from poe2scout.api.models import ApiModel
from poe2scout.db.repositories.models import CurrencyItemExtended, PriceLogEntry

from . import router


class GetCurrencyItemsResponse(ApiModel):
    class _Item(ApiModel):
        class _PriceLogEntry(ApiModel):
            price: float
            time: datetime
            quantity: int

            @classmethod
            def from_model(cls, model: PriceLogEntry) -> Self:
                return cls(
                    price=model.price,
                    time=model.time,
                    quantity=model.quantity,
                )

        id: int
        item_id: int
        currency_category_id: int
        api_id: str
        text: str
        category_api_id: str
        icon_url: str | None = None
        item_metadata: dict | None = None
        price_logs: list[_PriceLogEntry | None]
        current_price: float | None = None

        @classmethod
        def from_model(cls, model: CurrencyItemExtended) -> Self:
            return cls(
                id=model.id,
                item_id=model.itemId,
                currency_category_id=model.currencyCategoryId,
                api_id=model.apiId,
                text=model.text,
                category_api_id=model.categoryApiId,
                icon_url=model.iconUrl,
                item_metadata=model.itemMetadata,
                price_logs=[
                    cls._PriceLogEntry.from_model(price_log)
                    if price_log is not None
                    else None
                    for price_log in model.priceLogs
                ],
                current_price=model.currentPrice,
            )

    current_page: int
    pages: int
    total: int
    items: list[_Item]

    @classmethod
    def from_model(
        cls,
        current_page: int,
        pages: int,
        total: int,
        items: list[CurrencyItemExtended],
    ) -> Self:
        return cls(
            current_page=current_page,
            pages=pages,
            total=total,
            items=[cls._Item.from_model(item) for item in items],
        )


class GetCurrencyCategoryItemsRequest(ApiModel):
    category: str
    reference_currency: str
    search: str


def get_currency_category_items_request(
    category: Annotated[str, Path(alias="Category")],
    reference_currency: Annotated[
        str,
        Query(alias="ReferenceCurrency"),
    ] = "exalted",
    search: Annotated[str, Query(alias="Search")] = "",
) -> GetCurrencyCategoryItemsRequest:
    return GetCurrencyCategoryItemsRequest(
        category=category,
        reference_currency=reference_currency,
        search=search,
    )


GetCurrencyCategoryItemsRequestDep = Annotated[
    GetCurrencyCategoryItemsRequest,
    Depends(get_currency_category_items_request),
]


@router.get("/CurrencyCategory/{Category}")
async def get_currency_category_items(
    request: GetCurrencyCategoryItemsRequestDep,
    economy_cache: EconomyCacheDep,
    pagination: PaginationParamDep,
    item_repository: ItemRepoDep,
) -> GetCurrencyItemsResponse:
    if request.reference_currency not in ["exalted", "chaos"]:
        raise HTTPException(400, "reference currency must be exalted or chaos")

    league = await item_repository.GetLeagueByValue(pagination.league_name)

    if league is None:
        raise HTTPException(400, "Invalid league name")

    items = await economy_cache.GetCurrencyPage(
        league.id,
        request.category,
        request.reference_currency,
        search=request.search,
    )
    item_count = len(items)

    starting_index = (pagination.page - 1) * pagination.per_page
    ending_index = starting_index + pagination.per_page

    items = items[starting_index:ending_index]

    return GetCurrencyItemsResponse.from_model(
        current_page=pagination.page,
        pages=math.ceil(item_count / pagination.per_page),
        total=item_count,
        items=items,
    )
