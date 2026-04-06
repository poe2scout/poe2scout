from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories import currency_item_repository, item_repository, realm_repository
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
        icon_lookup: dict[str, str],
    ) -> Self:
        return cls(
            unique_categories=[
                cls._ItemCategory.from_model(
                    item_category=unique_category,
                    icon=icon_lookup.get(unique_category.api_id.lower(), ""),
                )
                for unique_category in unique_categories
            ],
            currency_categories=[
                cls._CurrencyCategory.from_model(
                    currency_category=currency_category,
                    icon=icon_lookup.get(currency_category.api_id.lower(), ""),
                )
                for currency_category in currency_categories
            ],
        )
    
class GetCategoriesRequest(ApiModel):
    realm: str    

def get_categories_request(
    realm: Annotated[str, Path(alias="Realm")],
) -> GetCategoriesRequest:
    return GetCategoriesRequest(
        realm=realm
    )


GetCategoriesRequestDep = Annotated[
    GetCategoriesRequest,
    Depends(get_categories_request),
]


@router.get("/Categories")
async def get_categories(
    request: GetCategoriesRequestDep
) -> GetCategoriesResponse:
    realm = await realm_repository.get_realm(request.realm)

    if realm is None:
        raise HTTPException(400, "Invalid realm")

    all_currency_categories = await currency_item_repository.get_all_currency_categories()
    all_item_categories = await item_repository.get_all_item_categories()

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
        icon_lookup=icon_dump(),
    )


def icon_dump() -> dict[str, str]:
    return {
        "delirium": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvRGlzdGlsbGVkRW1vdGlvbnMvRGlzdGlsbGVkRGVzcGFpciIsInciOjEsImgiOjEsInNjYWxlIjoxLCJyZWFsbSI6InBvZTIifV0/794fb40302/DistilledDespair.png",
        "fragments": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQnJlYWNoL0JyZWFjaHN0b25lU3BsaW50ZXIiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/00c84e43a8/BreachstoneSplinter.png",
        "map": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvUXVlc3RJdGVtcy9QaW5uYWNsZUtleTEiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/0d3dddab3b/PinnacleKey1.png",
        "ritual": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvT21lbnMvVm9vZG9vT21lbnMxUmVkIiwidyI6MSwiaCI6MSwic2NhbGUiOjEsInJlYWxtIjoicG9lMiJ9XQ/1c90d2eb1f/VoodooOmens1Red.png",
        "runes": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvUnVuZXMvQ29sZFJ1bmUiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/d3d9117ff2/ColdRune.png",
        "ultimatum": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvU291bENvcmVzL0dyZWF0ZXJTb3VsQ29yZUNyaXQiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/6d3a52eb08/GreaterSoulCoreCrit.png",
        "essences": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvRXNzZW5jZS9BdHRyaWJ1dGVFc3NlbmNlIiwidyI6MSwiaCI6MSwic2NhbGUiOjEsInJlYWxtIjoicG9lMiJ9XQ/7ee5c92c60/AttributeEssence.png",
        "currency": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lEdXBsaWNhdGUiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/b7f5cc7884/CurrencyDuplicate.png",
        "expedition": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvRXhwZWRpdGlvbi9CYXJ0ZXJSZWZyZXNoQ3VycmVuY3kiLCJ3IjoxLCJoIjoxLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/b0f42eaf8d/BarterRefreshCurrency.png",
        "breach": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQnJlYWNoL0JyZWFjaENhdGFseXN0RmlyZSIsInciOjEsImgiOjEsInNjYWxlIjoxLCJyZWFsbSI6InBvZTIifV0/156de12dd6/BreachCatalystFire.png",
        "breachcatalyst": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQnJlYWNoL0JyZWFjaENhdGFseXN0RmlyZSIsInciOjEsImgiOjEsInNjYWxlIjoxLCJyZWFsbSI6InBvZTIifV0/156de12dd6/BreachCatalystFire.png",
        "jewel": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvSmV3ZWxzL0JyZWFjaEpld2VsIiwidyI6MSwiaCI6MSwic2NhbGUiOjEsInJlYWxtIjoicG9lMiJ9XQ/9c17747ff2/BreachJewel.png",
        "accessory": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvUmluZ3MvTWlycm9yUmluZyIsInciOjEsImgiOjEsInNjYWxlIjoxLCJyZWFsbSI6InBvZTIiLCJkdXBsaWNhdGVkIjp0cnVlfV0/ec1c789fca/MirrorRing.png",
        "sanctum": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvUmVsaWNzL1JlbGljVW5pcXVlM3gxIiwidyI6MywiaCI6MSwic2NhbGUiOjEsInJlYWxtIjoicG9lMiJ9XQ/0fd744ac28/RelicUnique3x1.png",
        "weapon": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvV2VhcG9ucy9Ud29IYW5kV2VhcG9ucy9Ud29IYW5kTWFjZXMvVW5pcXVlcy9DaG9iZXJDaGFiZXIiLCJ3IjoyLCJoIjo0LCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/3de5003fa3/ChoberChaber.png",
        "flask": "https://web.poecdn.com/gen/image/WzksMTQseyJmIjoiMkRJdGVtcy9GbGFza3MvVW5pcXVlcy9NZWx0aW5nTWFlbHN0cm9tIiwidyI6MSwiaCI6Miwic2NhbGUiOjEsInJlYWxtIjoicG9lMiIsImxldmVsIjoxfV0/3ffec91606/MeltingMaelstrom.png",
        "armour": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQXJtb3Vycy9IZWxtZXRzL1VuaXF1ZXMvQ3Jvd25PZlRoZVZpY3RvciIsInciOjIsImgiOjIsInNjYWxlIjoxLCJyZWFsbSI6InBvZTIifV0/8397c94ec0/CrownOfTheVictor.png",
        "waystones": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvUHJlY3Vyc29yVGFibGV0cy9QcmVjdXJzb3JUYWJsZXRHZW5lcmljIiwic2NhbGUiOjEsInJlYWxtIjoicG9lMiJ9XQ/5658ce7f2d/PrecursorTabletGeneric.png",
        "talismans": "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvVG9ybWVudGVkU3Bpcml0U29ja2V0YWJsZXMvQXptZXJpU29ja2V0YWJsZU93bCIsInNjYWxlIjoxLCJyZWFsbSI6InBvZTIifV0/dfe1212549/AzmeriSocketableOwl.png",
        "vaultkeys": "https://web.poecdn.com//gen/image/WzI4LDE0LHsiZiI6IjJESXRlbXMvTWFwcy9Ud2lsaWdodE9yZGVyUmVsaXF1YXJ5S2V5V29ybGQiLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/11ce1d0bfd/TwilightOrderReliquaryKeyWorld.png",
        "abyss": "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQWJ5c3MvUHJlc2VydmVkSmF3Ym9uZSIsInNjYWxlIjoxLCJyZWFsbSI6InBvZTIifV0/2bb7939b21/PreservedJawbone.png",
        "uncutgems": "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9VbmN1dFNraWxsR2VtQnVmZiIsInNjYWxlIjoxLCJyZWFsbSI6InBvZTIifV0/ab25e9aa3b/UncutSkillGemBuff.png",
        "lineagesupportgems": "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvR2Vtcy9OZXcvTmV3U3VwcG9ydC9MaW5lYWdlL0xpbmVhZ2VWaWxlbnRhIiwic2NhbGUiOjEsInJlYWxtIjoicG9lMiJ9XQ/abda900f3c/LineageVilenta.png",
        "incursion": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvSW5jdXJzaW9uQ3JhZnRpbmdPcmJzL0luY3Vyc2lvbkdyZWF0ZXJWYWFsT3JiIiwic2NhbGUiOjEsInJlYWxtIjoicG9lMiJ9XQ/7ba6f79f63/IncursionGreaterVaalOrb.png",
        "idol": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvVG9ybWVudGVkU3Bpcml0U29ja2V0YWJsZXMvQXptZXJpU29ja2V0YWJsZU93bCIsInNjYWxlIjoxLCJyZWFsbSI6InBvZTIifV0/dfe1212549/AzmeriSocketableOwl.png",
    }
