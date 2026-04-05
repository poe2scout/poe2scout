from datetime import datetime, timezone
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query

from poe2scout.api.dependancies import (
    CurrencyItemRepoDep, 
    ItemRepoDep, 
    LeagueRepoDep, 
    PriceLogRepoDep
)
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories.price_log_repository.get_item_price_history import (
    GetItemPriceHistoryModel,
)
from poe2scout.db.repositories.models import PriceLogEntry

from ..leagues import router


class GetPriceHistoryRequest(ApiModel):
    item_id: int
    league_name: str
    log_count: int
    end_time: datetime
    reference_currency: str


def get_price_history_request(
    league_name: Annotated[str, Path(alias="LeagueName")],
    item_id: Annotated[int, Path(alias="ItemId")],
    log_count: Annotated[int, Query(alias="LogCount")],
    end_time: Annotated[datetime | None, Query(alias="EndTime")] = None,
    reference_currency: Annotated[str, Query(alias="ReferenceCurrency")] = "exalted",
) -> GetPriceHistoryRequest:
    return GetPriceHistoryRequest(
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
    request: GetPriceHistoryRequestDep,
    item_repository: ItemRepoDep,
    league_repository: LeagueRepoDep,
    currency_item_repository: CurrencyItemRepoDep,
    price_log_repository: PriceLogRepoDep
) -> GetPriceHistoryResponse:
    if request.log_count % 4 != 0:
        raise HTTPException(400, "LogCount must be a multiple of 4")

    leagues = await league_repository.get_all_leagues()
    league_id = next(
        (league.league_id for league in leagues if league.value == request.league_name),
        None,
    )

    if league_id is None:
        raise HTTPException(400, "League does not exist")

    log_frequency = 1 if await currency_item_repository.is_item_a_currency(request.item_id) else 6

    history = await price_log_repository.get_item_price_history(
        request.item_id,
        league_id,
        request.log_count,
        log_frequency,
        request.end_time,
    )

    if request.reference_currency != "exalted":
        reference_currency_item = await currency_item_repository.get_currency_item(
            request.reference_currency
        )

        if reference_currency_item is None:
            raise HTTPException(400, "Reference currency does not exist")

        reference_currency_history = await price_log_repository.get_item_price_history(
            reference_currency_item.item_id,
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

    return GetPriceHistoryResponse.from_model(history)
