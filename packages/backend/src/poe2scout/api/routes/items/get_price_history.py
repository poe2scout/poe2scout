from datetime import datetime, timezone
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories import (
    currency_item_repository,
    league_repository,
    price_log_repository,
    realm_repository,
)
from poe2scout.db.repositories.price_log_repository.get_item_price_history import (
    GetItemPriceHistoryModel,
)
from poe2scout.db.repositories.models import PriceLogEntry
from poe2scout.services.pricing import (
    convert_price_history_from_base,
    resolve_reference_currency_api_id,
)

from ..leagues import router


class GetPriceHistoryRequest(ApiModel):
    realm: str
    item_id: int
    league_name: str
    log_count: int
    end_time: datetime
    reference_currency: str | None


def get_price_history_request(
    realm: Annotated[str, Path(alias="Realm")],
    league_name: Annotated[str, Path(alias="LeagueName")],
    item_id: Annotated[int, Path(alias="ItemId")],
    log_count: Annotated[int, Query(alias="LogCount")],
    end_time: Annotated[datetime | None, Query(alias="EndTime")] = None,
    reference_currency: Annotated[str | None, Query(alias="ReferenceCurrency")] = None,
) -> GetPriceHistoryRequest:
    return GetPriceHistoryRequest(
        realm=realm,
        item_id=item_id,
        league_name=league_name,
        log_count=log_count,
        end_time=datetime.now(tz=timezone.utc) if end_time is None else end_time,
        reference_currency=reference_currency,
    )


GetPriceHistoryRequestDep = Annotated[
    GetPriceHistoryRequest,
    Depends(get_price_history_request),
]


class GetPriceHistoryResponse(ApiModel):
    class _PricePoint(ApiModel):
        price: float
        time: datetime
        quantity: int

        @classmethod
        def from_model(cls, price_point: PriceLogEntry) -> Self:
            return cls(
                price=price_point.price,
                time=price_point.time,
                quantity=price_point.quantity,
            )

    price_history: list[_PricePoint]
    has_more: bool

    @classmethod
    def from_model(cls, history: GetItemPriceHistoryModel) -> Self:
        return cls(
            price_history=[
                cls._PricePoint.from_model(price_point)
                for price_point in history.price_history
            ],
            has_more=history.has_more,
        )


@router.get("/{LeagueName}/Items/{ItemId}/History")
async def get_price_history(
    request: GetPriceHistoryRequestDep
) -> GetPriceHistoryResponse:
    realm = await realm_repository.get_realm(request.realm)

    if request.log_count % 4 != 0:
        raise HTTPException(400, "LogCount must be a multiple of 4")

    league = await league_repository.get_league_by_value(request.league_name, realm.game_id)

    if league is None:
        raise HTTPException(400, "League does not exist")

    log_frequency = (
        1 if await currency_item_repository.is_item_a_currency(request.item_id) else 6
    )

    history = await price_log_repository.get_item_price_history(
        request.item_id,
        league.league_id,
        realm.realm_id,
        request.log_count,
        log_frequency,
        request.end_time,
    )

    reference_currency_api_id = resolve_reference_currency_api_id(
        request.reference_currency,
        league.base_currency_api_id,
    )

    if reference_currency_api_id != league.base_currency_api_id:
        reference_currency_item = await currency_item_repository.get_currency_item(
            reference_currency_api_id,
            realm.game_id
        )

        if reference_currency_item is None:
            raise HTTPException(400, "Reference currency does not exist")

        reference_currency_history = await price_log_repository.get_item_price_history(
            reference_currency_item.item_id,
            league.league_id,
            realm.realm_id,
            request.log_count,
            log_frequency,
            request.end_time,
        )

        history = GetItemPriceHistoryModel(
            price_history=convert_price_history_from_base(
                history.price_history,
                reference_currency_history.price_history,
            ),
            has_more=history.has_more,
        )

    return GetPriceHistoryResponse.from_model(history)
