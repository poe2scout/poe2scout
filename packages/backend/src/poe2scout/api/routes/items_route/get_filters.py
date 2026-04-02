from typing import Self

from pydantic import BaseModel

from poe2scout.db.repositories.item_repository.GetSearchOptions import SearchOption

from . import router
from fastapi import Depends
from poe2scout.api.dependancies import get_item_repository
from poe2scout.db.repositories import ItemRepository

class GetFiltersResponse(BaseModel):
    class _SearchOption(BaseModel):
        display_name: str
        category: str
        identifier: str

        @classmethod
        def from_model(cls, filter: SearchOption) -> Self:
            return cls(
                display_name=filter.display_name,
                category=filter.category,
                identifier=filter.identifier
            )


    filters: list[_SearchOption]

    @classmethod
    def from_model(cls, filters: list[SearchOption]) -> Self:
        return cls(
            filters=[cls._SearchOption.from_model(filter) for filter in filters]
        )

@router.get("/Filters")
async def get_filters(
    item_repository: ItemRepository = Depends(get_item_repository)
):
    return GetFiltersResponse.from_model(await item_repository.GetSearchOptions())
