from datetime import datetime
from typing import Self

from poe2scout.api.dependancies import ItemRepoDep
from poe2scout.api.models import ApiModel
from poe2scout.db.repositories.models import CurrencyItemExtended, PriceLogEntry

from . import router

IMPORTANT_API_IDS = ["mirror", "divine", "exalted", "annul"]
DEFAULT_LEAGUE_ID = 7


class GetLandingSplashInfoResponse(ApiModel):
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

    items: list[_Item]

    @classmethod
    def from_model(cls, model: list[CurrencyItemExtended]) -> Self:
        return cls(items=[cls._Item.from_model(item) for item in model])


@router.get("/LandingSplashInfo")
async def get_landing_splash_info(
    item_repository: ItemRepoDep,
) -> GetLandingSplashInfoResponse:
    items = await item_repository.GetCurrencyItems(IMPORTANT_API_IDS)

    item_ids = [item.itemId for item in items]

    price_logs = await item_repository.GetItemPriceLogs(item_ids, DEFAULT_LEAGUE_ID)

    items = [
        CurrencyItemExtended(**item.model_dump(), priceLogs=price_logs[item.itemId])
        for item in items
    ]

    last_price = dict.fromkeys(item_ids, 0.0)

    for item in items:
        for log in item.priceLogs:
            if log is not None and hasattr(log, "price"):
                last_price[item.itemId] = log.price
                break

    items.sort(
        key=lambda item: int(last_price[item.itemId]) if item.itemId in last_price else 0,
        reverse=True,
    )

    return GetLandingSplashInfoResponse.from_model(items)
