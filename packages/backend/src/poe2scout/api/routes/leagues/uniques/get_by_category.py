import math
from datetime import datetime
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query

from poe2scout.api.dependancies import EconomyCacheDep, ItemRepoDep, PaginationParamDep
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories.models import PriceLogEntry, UniqueItemExtended

from .. import router

class GetUniqueItemsResponse(ApiModel):
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
        icon_url: str | None = None
        text: str
        name: str
        category_api_id: str
        item_metadata: dict | None = None
        type: str
        is_chanceable: bool | None = False
        price_logs: list[_PriceLogEntry | None]
        current_price: float | None = None

        @classmethod
        def from_model(cls, model: UniqueItemExtended) -> Self:
            return cls(
                id=model.id,
                item_id=model.item_id,
                icon_url=model.icon_url,
                text=model.text,
                name=model.name,
                category_api_id=model.category_api_id,
                item_metadata=model.item_metadata,
                type=model.type,
                is_chanceable=model.is_chanceable,
                price_logs=[
                    cls._PriceLogEntry.from_model(log) if log is not None else None
                    for log in model.price_logs
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
        items: list[UniqueItemExtended],
    ) -> Self:
        return cls(
            current_page=current_page,
            pages=pages,
            total=total,
            items=[cls._Item.from_model(item) for item in items],
        )


class GetUniqueCategoryItemsRequest(ApiModel):
    league_name: str
    category: str
    reference_currency: str
    search: str


def get_unique_category_items_request(
    league_name: Annotated[str, Path(alias="LeagueName")],
    category: Annotated[str, Query(alias="Category")],
    reference_currency: Annotated[
        str,
        Query(alias="ReferenceCurrency"),
    ] = "exalted",
    search: Annotated[str, Query(alias="Search")] = "",
) -> GetUniqueCategoryItemsRequest:
    return GetUniqueCategoryItemsRequest(
        league_name=league_name,
        category=category,
        reference_currency=reference_currency,
        search=search,
    )


GetUniqueCategoryItemsRequestDep = Annotated[
    GetUniqueCategoryItemsRequest,
    Depends(get_unique_category_items_request),
]


@router.get("/{LeagueName}/Uniques/ByCategory")
async def get_unique_category_items(
    request: GetUniqueCategoryItemsRequestDep,
    pagination: PaginationParamDep,
    repo: ItemRepoDep,
    economy_cache: EconomyCacheDep,
) -> GetUniqueItemsResponse:
    if request.reference_currency not in ["exalted", "chaos"]:
        raise HTTPException(400, "reference currency must be exalted or chaos")

    league = await repo.get_league_by_value(request.league_name)
    if league is None:
        raise HTTPException(400, "Invalid league name")

    items = await economy_cache.get_unique_page(
        league.id,
        request.category,
        request.reference_currency,
        request.search,
    )
    item_count = len(items)

    starting_index = (pagination.page - 1) * pagination.per_page
    ending_index = starting_index + pagination.per_page

    items = items[starting_index:ending_index]

    return GetUniqueItemsResponse.from_model(
        current_page=pagination.page,
        pages=math.ceil(item_count / pagination.per_page),
        total=item_count,
        items=items,
    )
