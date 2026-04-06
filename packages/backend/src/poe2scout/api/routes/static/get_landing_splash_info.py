from datetime import datetime
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories import (
    currency_item_repository, 
    game_repository, 
    price_log_repository, 
    realm_repository
)
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

        currency_item_id: int
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
                currency_item_id=model.currency_item_id,
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


class GetLandingSplashInfoRequest(ApiModel):
    realm: str


def get_landing_splash_info_request(
    realm: Annotated[str, Path(alias="Realm")],
) -> GetLandingSplashInfoRequest:
    return GetLandingSplashInfoRequest(realm=realm)


GetLandingSplashInfoRequestDep = Annotated[
    GetLandingSplashInfoRequest,
    Depends(get_landing_splash_info_request),
]


@router.get("/LandingSplashInfo")
async def get_landing_splash_info(
    request: GetLandingSplashInfoRequestDep,
) -> GetLandingSplashInfoResponse:
    realm = await realm_repository.get_realm(request.realm)

    if realm is None:
        raise HTTPException(400, "Invalid realm")

    items = await currency_item_repository.get_currency_items(IMPORTANT_API_IDS, realm.game_id)

    item_ids = [item.item_id for item in items]

    default_league_id = await game_repository.get_default_league(realm.game_id)

    price_logs = await price_log_repository.get_item_price_logs(
        item_ids, 
        default_league_id,
        realm.realm_id
    )

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
