import math
from datetime import datetime
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query

from poe2scout.api.dependancies import EconomyCacheDep, LeagueRepoDep, PaginationParamDep
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories.models import CurrencyItemExtended, PriceLogEntry

from .. import router


class GetByCategoryResponse(ApiModel):
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

        currency_item_id: int
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
                currency_item_id=model.currency_item_id,
                item_id=model.item_id,
                currency_category_id=model.currency_category_id,
                api_id=model.api_id,
                text=model.text,
                category_api_id=model.category_api_id,
                icon_url=model.icon_url,
                item_metadata=model.item_metadata,
                price_logs=[
                    cls._PriceLogEntry.from_model(price_log)
                    if price_log is not None
                    else None
                    for price_log in model.price_logs
                ],
                current_price=model.current_price,
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


class GetByCategoryRequest(ApiModel):
    league_name: str
    category: str
    reference_currency: str
    search: str


def get_by_category_request(
    league_name: Annotated[str, Path(alias="LeagueName")],
    category: Annotated[str, Query(alias="Category")],
    reference_currency: Annotated[
        str,
        Query(alias="ReferenceCurrency"),
    ] = "exalted",
    search: Annotated[str, Query(alias="Search")] = "",
) -> GetByCategoryRequest:
    return GetByCategoryRequest(
        league_name=league_name,
        category=category,
        reference_currency=reference_currency,
        search=search,
    )


GetByCategoryRequestDep = Annotated[
    GetByCategoryRequest,
    Depends(get_by_category_request),
]


@router.get("/{LeagueName}/Currencies/ByCategory")
async def get_by_category(
    request: GetByCategoryRequestDep,
    economy_cache: EconomyCacheDep,
    pagination: PaginationParamDep,
    league_repository: LeagueRepoDep,
) -> GetByCategoryResponse:
    if request.reference_currency not in ["exalted", "chaos"]:
        raise HTTPException(400, "reference currency must be exalted or chaos")

    league = await league_repository.get_league_by_value(request.league_name)

    if league is None:
        raise HTTPException(400, "Invalid league name")

    items = await economy_cache.get_currency_page(
        league.league_id,
        request.category,
        request.reference_currency,
        search=request.search,
    )
    item_count = len(items)

    starting_index = (pagination.page - 1) * pagination.per_page
    ending_index = starting_index + pagination.per_page

    items = items[starting_index:ending_index]

    return GetByCategoryResponse.from_model(
        current_page=pagination.page,
        pages=math.ceil(item_count / pagination.per_page),
        total=item_count,
        items=items,
    )
