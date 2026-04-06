from datetime import datetime
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path

from poe2scout.api.api_model import ApiModel
from poe2scout.api.dependancies import cache_response
from poe2scout.db.repositories import (
    currency_item_repository,
    league_repository,
    price_log_repository,
    realm_repository,
)
from poe2scout.db.repositories.models import CurrencyItem, PriceLogEntry

from .. import router


class GetResponse(ApiModel):
    class _PriceLogEntry(ApiModel):
        price: float
        time: datetime
        quantity: int

        @classmethod
        def from_model(cls, price_log: PriceLogEntry) -> Self:
            return cls(
                price=price_log.price,
                time=price_log.time,
                quantity=price_log.quantity,
            )

    currency_item_id: int
    item_id: int
    currency_category_id: int
    api_id: str
    text: str
    category_api_id: str
    icon_url: str | None
    item_metadata: dict | None = None
    price_logs: list[_PriceLogEntry | None]
    current_price: float | None = None

    @classmethod
    def from_model(
        cls,
        currency_item: CurrencyItem,
        price_logs: list[PriceLogEntry | None],
    ) -> Self:
        return cls(
            currency_item_id=currency_item.currency_item_id,
            item_id=currency_item.item_id,
            currency_category_id=currency_item.currency_category_id,
            api_id=currency_item.api_id,
            text=currency_item.text,
            category_api_id=currency_item.category_api_id,
            icon_url=currency_item.icon_url,
            item_metadata=currency_item.item_metadata,
            price_logs=[
                cls._PriceLogEntry.from_model(price_log)
                if price_log is not None
                else None
                for price_log in price_logs
            ],
            current_price=next(
                (price_log.price for price_log in price_logs if price_log is not None),
                None,
            ),
        )


class GetRequest(ApiModel):
    realm: str
    api_id: str
    league_name: str


def get_request(
    realm: Annotated[str, Path(alias="Realm")],
    league_name: Annotated[str, Path(alias="LeagueName")],
    api_id: Annotated[str, Path(alias="ApiId")],
) -> GetRequest:
    return GetRequest(
        realm=realm,
        api_id=api_id,
        league_name=league_name,
    )


GetRequestDep = Annotated[
    GetRequest,
    Depends(get_request),
]


@router.get("/{LeagueName}/Currencies/{ApiId}")
@cache_response(
    key=lambda params: (
        f"get_currency_item:{params['request'].api_id}:{params['request'].league_name}"
    )
)
async def get(
    request: GetRequestDep,
) -> GetResponse:
    realm = await realm_repository.get_realm(request.realm)

    if realm is None:
        raise HTTPException(400, "Invalid realm")

    currency_item = await currency_item_repository.get_currency_item(request.api_id, realm.game_id)
    if currency_item is None:
        raise HTTPException(400, "Invalid currency item api ID")

    league = await league_repository.get_league_by_value(request.league_name, realm.game_id)
    if league is None:
        raise HTTPException(400, "Invalid league name")

    price_logs_by_item_id = await price_log_repository.get_item_price_logs(
        item_ids=[currency_item.item_id],
        league_id=league.league_id,
        realm_id=realm.realm_id
    )

    return GetResponse.from_model(
        currency_item,
        price_logs_by_item_id.get(currency_item.item_id, []),
    )
