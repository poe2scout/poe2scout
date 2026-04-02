from typing import Self

from poe2scout.api.dependancies import ItemRepoDep
from poe2scout.api.models import ApiModel
from poe2scout.db.repositories.item_repository.GetSearchOptions import SearchOption

from . import router


class GetFiltersResponse(ApiModel):
    class _SearchOption(ApiModel):
        display_name: str
        category: str
        identifier: str

        @classmethod
        def from_model(cls, filter_option: SearchOption) -> Self:
            return cls(
                display_name=filter_option.display_name,
                category=filter_option.category,
                identifier=filter_option.identifier,
            )

    filters: list[_SearchOption]

    @classmethod
    def from_model(cls, filters: list[SearchOption]) -> Self:
        return cls(
            filters=[cls._SearchOption.from_model(filter_option) for filter_option in filters]
        )


@router.get("/Filters")
async def get_filters(
    item_repository: ItemRepoDep,
) -> GetFiltersResponse:
    return GetFiltersResponse.from_model(await item_repository.GetSearchOptions())
