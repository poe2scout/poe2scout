import asyncio
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query
from poe2scout.api.api_model import ApiModel
from poe2scout.api.dependancies import cache_response
from poe2scout.db.repositories import (
    currency_item_repository,
    item_repository,
    league_repository,
    realm_repository,
)
from poe2scout.db.repositories.currency_item_repository.get_all_currency_categories import (
    CurrencyCategory
)
from poe2scout.db.repositories.item_repository.get_all_item_categories import ItemCategory

from . import router

IGNORE_CURRENCIES = ["gem", "relics", "waystones"]


class GetCategoriesResponse(ApiModel):
    class _ItemCategory(ApiModel):
        item_category_id: int
        api_id: str
        label: str
        icon: str

        @classmethod
        def from_model(
            cls,
            item_category: ItemCategory,
            icon: str,
        ) -> Self:
            return cls(
                item_category_id=item_category.item_category_id,
                api_id=item_category.api_id,
                label=item_category.label,
                icon=icon,
            )
        
    class _CurrencyCategory(ApiModel):
        currency_category_id: int
        api_id: str
        label: str
        icon: str

        @classmethod
        def from_model(
            cls,
            currency_category: CurrencyCategory,
            icon: str,
        ) -> Self:
            return cls(
                currency_category_id=currency_category.currency_category_id,
                api_id=currency_category.api_id,
                label=currency_category.label,
                icon=icon,
            )


    unique_categories: list[_ItemCategory]
    currency_categories: list[_CurrencyCategory]

    @classmethod
    def from_model(
        cls,
        unique_categories: list[ItemCategory],
        currency_categories: list[CurrencyCategory],
        unique_icon_lookup: dict[str, str],
        currency_icon_lookup: dict[str, str],
    ) -> Self:
        return cls(
            unique_categories=[
                cls._ItemCategory.from_model(
                    item_category=unique_category,
                    icon=unique_icon_lookup.get(unique_category.api_id, ""),
                )
                for unique_category in unique_categories
            ],
            currency_categories=[
                cls._CurrencyCategory.from_model(
                    currency_category=currency_category,
                    icon=currency_icon_lookup.get(currency_category.api_id, ""),
                )
                for currency_category in currency_categories
            ],
        )


class GetCategoriesRequest(ApiModel):
    realm: str
    league_name: str

def get_categories_request(
    realm: Annotated[str, Path(alias="Realm")],
    league_name: Annotated[str, Query(alias="LeagueName")],
) -> GetCategoriesRequest:
    return GetCategoriesRequest(
        realm=realm,
        league_name=league_name,
    )


GetCategoriesRequestDep = Annotated[
    GetCategoriesRequest,
    Depends(get_categories_request),
]


@router.get("/Categories")
@cache_response(
    key=lambda params: (
        f"get_categories:{params['request'].realm}:{params['request'].league_name}"
    ),
    ttl=60 * 10,
)
async def get_categories(
    request: GetCategoriesRequestDep
) -> GetCategoriesResponse:
    realm = await realm_repository.get_realm(request.realm)

    if realm is None:
        raise HTTPException(400, "Invalid realm")

    league = await league_repository.get_league_by_value(request.league_name, realm.game_id)

    if league is None:
        raise HTTPException(400, "Invalid league name")

    (
        all_currency_categories,
        all_item_categories,
        currency_icon_rows,
        unique_icon_rows,
    ) = await asyncio.gather(
        currency_item_repository.get_priced_currency_categories(
            league.league_id,
            realm.realm_id,
            realm.game_id,
        ),
        item_repository.get_priced_item_categories(
            league.league_id,
            realm.realm_id,
            realm.game_id,
        ),
        currency_item_repository.get_category_icons(realm.game_id),
        item_repository.get_category_icons(realm.game_id),
    )

    currency_icon_lookup = {icon.api_id: icon.icon_url for icon in currency_icon_rows}
    unique_icon_lookup = {icon.api_id: icon.icon_url for icon in unique_icon_rows}

    unique_item_categories = [
        category
        for category in all_item_categories
        if category.api_id != "currency" and category.api_id not in IGNORE_CURRENCIES
    ]

    currency_item_categories = [
        category
        for category in all_currency_categories
        if category.api_id not in IGNORE_CURRENCIES
    ]

    return GetCategoriesResponse.from_model(
        unique_categories=unique_item_categories,
        currency_categories=currency_item_categories,
        unique_icon_lookup=unique_icon_lookup,
        currency_icon_lookup=currency_icon_lookup,
    )
