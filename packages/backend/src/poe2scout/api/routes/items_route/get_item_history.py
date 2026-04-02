from datetime import datetime, timezone
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query
from pydantic import BaseModel

from poe2scout.api.dependancies import ItemRepoDep
from poe2scout.db.repositories.item_repository.GetItemPriceHistory import (
    GetItemPriceHistoryModel,
)
from poe2scout.db.repositories.models import PriceLogEntry

from . import router


class GetItemHistoryRequest(BaseModel):
    item_id: int
    league_name: str
    log_count: int
    end_time: datetime
    reference_currency: str


def get_item_history_request(
    item_id: Annotated[int, Path(alias="itemId")],
    league_name: Annotated[str, Query(alias="leagueName")],
    log_count: Annotated[int, Query(alias="logCount")],
    end_time: Annotated[datetime | None, Query(alias="endTime")] = None,
    reference_currency: Annotated[str, Query(alias="referenceCurrency")] = "exalted",
) -> GetItemHistoryRequest:
    return GetItemHistoryRequest(
        item_id=item_id,
        league_name=league_name,
        log_count=log_count,
        end_time=datetime.now(tz=timezone.utc) if end_time is None else end_time,
        reference_currency=reference_currency,
    )


GetItemHistoryRequestDep = Annotated[
    GetItemHistoryRequest,
    Depends(get_item_history_request),
]


class GetItemHistoryResponse(BaseModel):
    class _PricePoint(BaseModel):
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


@router.get("/{itemId}/History")
async def get_item_history(
    request: GetItemHistoryRequestDep,
    item_repository: ItemRepoDep,
) -> GetItemHistoryResponse:
    if request.log_count % 4 != 0:
        raise HTTPException(400, "logCount must be a multiple of 4")

    leagues = await item_repository.GetAllLeagues()
    league_id = next(
        (league.id for league in leagues if league.value == request.league_name),
        None,
    )

    if league_id is None:
        raise HTTPException(400, "League does not exist")

    log_frequency = 1 if await item_repository.IsItemACurrency(request.item_id) else 6

    history = await item_repository.GetItemPriceHistory(
        request.item_id,
        league_id,
        request.log_count,
        log_frequency,
        request.end_time,
    )

    if request.reference_currency != "exalted":
        reference_currency_item = await item_repository.GetCurrencyItem(
            request.reference_currency
        )

        if reference_currency_item is None:
            raise HTTPException(400, "Reference currency does not exist")

        reference_currency_history = await item_repository.GetItemPriceHistory(
            reference_currency_item.itemId,
            league_id,
            request.log_count,
            log_frequency,
            request.end_time,
        )

        reference_currency_history_lookup = {
            price_log.time: price_log
            for price_log in reference_currency_history.price_history
        }

        adjusted_price_history: list[PriceLogEntry] = []
        last_reference_price = 0.0

        for price_log in history.price_history:
            current_reference_log = reference_currency_history_lookup.get(
                price_log.time
            )

            if current_reference_log is not None:
                last_reference_price = current_reference_log.price

            if last_reference_price == 0:
                continue

            adjusted_price_history.append(
                PriceLogEntry(
                    price=price_log.price / last_reference_price,
                    time=price_log.time,
                    quantity=price_log.quantity,
                )
            )

        history = GetItemPriceHistoryModel(
            price_history=adjusted_price_history,
            has_more=history.has_more,
        )

    return GetItemHistoryResponse.from_model(history)
