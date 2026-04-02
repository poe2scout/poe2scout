from datetime import datetime
from typing import Optional, Self

from poe2scout.db.repositories.models import PriceLogEntry

from . import router
from poe2scout.api.dependancies import ItemRepoDep

from poe2scout.api.routes.item_route.get_currency_category_items import (
    CurrencyItemExtended
)

from pydantic import BaseModel

important_api_ids = ["mirror", "divine", "exalted", "annul"]
default_league_id = 7

class GetLandingSplashInfoResponse(BaseModel):
    class _Item(BaseModel):
        class _PriceLogEntry(BaseModel):
            price: float
            time: datetime
            quantity: int

            @classmethod
            def from_model(cls, model: PriceLogEntry) -> Self:
                return cls(
                    price=model.price,
                    time=model.time,
                    quantity=model.quantity
                )

        id: int
        item_id: int
        currency_category_id: int
        api_id: str
        text: str
        category_api_id: str
        icon_url: Optional[str] = None
        item_metadata: Optional[dict] = None
        price_logs: list[_PriceLogEntry | None]
        current_price: Optional[float] = None

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
                current_price=model.currentPrice
            )

    items: list[_Item]

    @classmethod
    def from_model(cls, model: list[CurrencyItemExtended]) -> Self:
        return cls(
            items=[cls._Item.from_model(item) for item in model]
        )

@router.get("/LandingSplashInfo")
async def get_landing_splash_info(
    item_repository: ItemRepoDep,
) -> GetLandingSplashInfoResponse:
    items = await item_repository.GetCurrencyItems(important_api_ids)

    itemIds = [item.itemId for item in items]

    priceLogs = await item_repository.GetItemPriceLogs(itemIds, default_league_id)

    items = [
        CurrencyItemExtended(**item.model_dump(), priceLogs=priceLogs[item.itemId])
        for item in items
    ]

    lastPrice = dict.fromkeys(itemIds, 0.0)

    for item in items:
        for log in item.priceLogs:
            if log and hasattr(log, "price"):
                lastPrice[item.itemId] = log.price
                break

    items.sort(
        key=lambda item: (
            int(lastPrice[item.itemId]) if item.itemId in lastPrice else 0.0
        ),
        reverse=True,
    )

    return GetLandingSplashInfoResponse.from_model(items)
