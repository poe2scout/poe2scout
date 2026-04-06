from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories import item_repository, realm_repository
from poe2scout.db.repositories.item_repository.get_search_options import SearchOption

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


class GetFiltersRequest(ApiModel):
    realm: str


def get_filters_request(
    realm: Annotated[str, Path(alias="Realm")],
) -> GetFiltersRequest:
    return GetFiltersRequest(realm=realm)


GetFiltersRequestDep = Annotated[
    GetFiltersRequest,
    Depends(get_filters_request),
]


@router.get("/Filters")
async def get_filters(
    request: GetFiltersRequestDep,
) -> GetFiltersResponse:
    realm = await realm_repository.get_realm(request.realm)

    if realm is None:
        raise HTTPException(400, "Invalid realm")

    return GetFiltersResponse.from_model(await item_repository.get_search_options(realm.game_id))
