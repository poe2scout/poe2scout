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

    items: list[_Item]

    @classmethod
    def from_model(cls, model: list[CurrencyItemExtended]) -> Self:
        return cls(items=[cls._Item.from_model(item) for item in model])


@router.get("/LandingSplashInfo")
async def get_landing_splash_info(
    item_repository: ItemRepoDep,
) -> GetLandingSplashInfoResponse:
    items = await item_repository.get_currency_items(IMPORTANT_API_IDS)

    item_ids = [item.item_id for item in items]

    price_logs = await item_repository.get_item_price_logs(item_ids, DEFAULT_LEAGUE_ID)

    items = [
        CurrencyItemExtended(**item.model_dump(), price_logs=price_logs[item.item_id])
        for item in items
    ]

    last_price = dict.fromkeys(item_ids, 0.0)

    for item in items:
        for log in item.price_logs:
            if log is not None and hasattr(log, "price"):
                last_price[item.item_id] = log.price
                break

    items.sort(
        key=lambda item: int(last_price[item.item_id]) if item.item_id in last_price else 0,
        reverse=True,
    )

    return GetLandingSplashInfoResponse.from_model(items)
