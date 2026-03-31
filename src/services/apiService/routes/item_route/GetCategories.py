from fastapi import Depends

from . import router
from services.apiService.dependancies import get_item_repository
from services.repositories import ItemRepository
from pydantic import BaseModel


class Category(BaseModel):
    id: int
    apiId: str
    label: str
    icon: str


class CategoryResponse(BaseModel):
    unique_categories: list[Category]
    currency_categories: list[Category]


ignoreCurrencies = ["gem", "relics", "waystones"]


@router.get("/categories")
async def GetCategories(
    item_repository: ItemRepository = Depends(get_item_repository),
) -> CategoryResponse:
    currencyCategories = await item_repository.GetAllCurrencyCategories()
    uniqueCategories = await item_repository.GetAllItemCategories()

    icons = icon_dump()

    uniqueCategories = [
        Category(
            **uniqueCategory.model_dump(),
            icon=icons[uniqueCategory.apiId.lower()]
            if uniqueCategory.apiId.lower() in icons
            else "",
        )
        for uniqueCategory in uniqueCategories
        if uniqueCategory.apiId != "currency"
    ]
    currencyCategories = [
        Category(
            **currencyCategory.model_dump(),
            icon=icons[currencyCategory.apiId.lower()]
            if currencyCategory.apiId.lower() in icons
            else "",
        )
        for currencyCategory in currencyCategories
        if currencyCategory.apiId not in ignoreCurrencies
    ]

    uniqueCategories = [
        cat for cat in uniqueCategories if cat.apiId not in ignoreCurrencies
    ]
    currencyCategories = [
        cat for cat in currencyCategories if cat.apiId not in ignoreCurrencies
    ]

    return CategoryResponse(
        unique_categories=uniqueCategories, currency_categories=currencyCategories
    )


def icon_dump():
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
        "idol": "https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvVG9ybWVudGVkU3Bpcml0U29ja2V0YWJsZXMvQXptZXJpU29ja2V0YWJsZU93bCIsInNjYWxlIjoxLCJyZWFsbSI6InBvZTIifV0/dfe1212549/AzmeriSocketableOwl.png"
    }
