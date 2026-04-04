from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Query

from poe2scout.api.dependancies import CXRepoDep, ItemRepoDep
from poe2scout.api.models import ApiModel
from poe2scout.db.repositories.currency_exchange_repository.get_pair_history import (
    GetCurrentSnapshotPairModel,
    GetPairHistoryModel,
    PairData,
    PairDataDetails,
)

from . import router


class GetPairHistoryRequest(ApiModel):
    league_name: str
    currency_one_item_id: int
    currency_two_item_id: int
    limit: int
    end_epoch: int | None


def get_pair_history_request(
    league_name: Annotated[str, Query(alias="LeagueName")],
    currency_one_item_id: Annotated[int, Query(alias="CurrencyOneItemId")],
    currency_two_item_id: Annotated[int, Query(alias="CurrencyTwoItemId")],
    limit: Annotated[int, Query(alias="Limit")],
    end_epoch: Annotated[int | None, Query(alias="EndEpoch")] = None,
) -> GetPairHistoryRequest:
    return GetPairHistoryRequest(
        league_name=league_name,
        currency_one_item_id=currency_one_item_id,
        currency_two_item_id=currency_two_item_id,
        limit=limit,
        end_epoch=end_epoch,
    )


GetPairHistoryRequestDep = Annotated[
    GetPairHistoryRequest,
    Depends(get_pair_history_request),
]


class GetPairHistoryResponse(ApiModel):
    class _Meta(ApiModel):
        has_more: bool

        @classmethod
        def from_model(cls, meta: dict[str, object]) -> Self:
            return cls(has_more=bool(meta.get("has_more", False)))

    class _Pair(ApiModel):
        class _Data(ApiModel):
            class _Details(ApiModel):
                currency_item_id: int
                value_traded: Decimal
                relative_price: Decimal
                stock_value: Decimal
                volume_traded: int
                highest_stock: int

                @classmethod
                def from_model(cls, model: PairDataDetails) -> Self:
                    return cls(
                        currency_item_id=model.currency_item_id,
                        value_traded=model.value_traded,
                        relative_price=model.relative_price,
                        stock_value=model.stock_value,
                        volume_traded=model.volume_traded,
                        highest_stock=model.highest_stock,
                    )

            currency_one_data: _Details
            currency_two_data: _Details

            @classmethod
            def from_model(cls, model: PairData) -> Self:
                return cls(
                    currency_one_data=cls._Details.from_model(model.currency_one_data),
                    currency_two_data=cls._Details.from_model(model.currency_two_data),
                )

        epoch: int
        data: _Data

        @classmethod
        def from_model(cls, model: GetCurrentSnapshotPairModel) -> Self:
            return cls(
                epoch=model.epoch,
                data=cls._Data.from_model(model.data),
            )

    history: list[_Pair]
    meta: _Meta

    @classmethod
    def from_model(cls, model: GetPairHistoryModel) -> Self:
        return cls(
            history=[cls._Pair.from_model(history) for history in model.history],
            meta=cls._Meta.from_model(model.meta),
        )


@router.get("/PairHistory")
async def get_pair_history(
    request: GetPairHistoryRequestDep,
    item_repository: ItemRepoDep,
    currency_exchange_repository: CXRepoDep,
) -> GetPairHistoryResponse:
    league = await item_repository.get_league_by_value(request.league_name)

    if league is None:
        raise HTTPException(400, "Invalid league name")

    pair_history = await currency_exchange_repository.get_pair_history(
        request.currency_one_item_id,
        request.currency_two_item_id,
        league.id,
        request.end_epoch
        if request.end_epoch is not None
        else int(datetime.now(tz=timezone.utc).timestamp()),
        request.limit,
    )

    if pair_history is None:
        raise HTTPException(404, "No data for given league.")

    return GetPairHistoryResponse.from_model(pair_history)
