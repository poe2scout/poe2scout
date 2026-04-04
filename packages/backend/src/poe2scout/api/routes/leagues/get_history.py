from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query

from poe2scout.api.dependancies import CXRepoDep, ItemRepoDep
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories.currency_exchange_repository.get_current_snapshot_history import (
    GetCurrencyExchangeHistoryData,
    GetCurrencyExchangeHistoryModel,
)

from . import router


class GetSnapshotHistoryRequest(ApiModel):
    league_name: str
    limit: int
    end_epoch: int | None


def get_snapshot_history_request(
    league_name: Annotated[str, Path(alias="LeagueName")],
    limit: Annotated[int, Query(alias="Limit")],
    end_epoch: Annotated[int | None, Query(alias="EndEpoch")] = None,
) -> GetSnapshotHistoryRequest:
    return GetSnapshotHistoryRequest(
        league_name=league_name,
        limit=limit,
        end_epoch=end_epoch,
    )


GetSnapshotHistoryRequestDep = Annotated[
    GetSnapshotHistoryRequest,
    Depends(get_snapshot_history_request),
]


class GetSnapshotHistoryResponse(ApiModel):
    class _Data(ApiModel):
        epoch: int
        market_cap: Decimal
        volume: Decimal

        @classmethod
        def from_model(cls, model: GetCurrencyExchangeHistoryData) -> Self:
            return cls(
                epoch=model.epoch,
                market_cap=Decimal(model.market_cap),
                volume=Decimal(model.volume),
            )

    class _Meta(ApiModel):
        has_more: bool

        @classmethod
        def from_model(cls, meta: dict[str, bool]) -> Self:
            return cls(has_more=meta.get("has_more", False))

    data: list[_Data]
    meta: _Meta

    @classmethod
    def from_model(cls, model: GetCurrencyExchangeHistoryModel) -> Self:
        return cls(
            data=[cls._Data.from_model(entry) for entry in model.data],
            meta=cls._Meta.from_model(model.meta),
        )


@router.get("/{LeagueName}/SnapshotHistory")
async def get_snapshot_history(
    request: GetSnapshotHistoryRequestDep,
    item_repository: ItemRepoDep,
    currency_exchange_repository: CXRepoDep,
) -> GetSnapshotHistoryResponse:
    league = await item_repository.get_league_by_value(request.league_name)

    if league is None:
        raise HTTPException(400, "Invalid league name")

    snapshot_history = await currency_exchange_repository.get_currency_exchange_history(
        league.id,
        request.end_epoch
        if request.end_epoch is not None
        else int(datetime.now(tz=timezone.utc).timestamp()),
        request.limit,
    )

    if snapshot_history is None:
        raise HTTPException(404, "No data for given league.")

    return GetSnapshotHistoryResponse.from_model(snapshot_history)
