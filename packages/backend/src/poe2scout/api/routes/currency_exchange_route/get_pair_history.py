from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel
from poe2scout.db.repositories.currency_exchange_repository.GetPairHistory import (
    GetCurrentSnapshotPairModel,
    GetPairHistoryModel,
    PairData,
    PairDataDetails,
)
from . import router
from fastapi import HTTPException, Query
from poe2scout.api.dependancies import CXRepoDep, ItemRepoDep

class GetPairHistoryRequest(BaseModel):
    league_name: str
    currency_one_item_id: int
    currency_two_item_id: int
    limit: int
    end_epoch: int | None

def get_pair_history_request(
    league_name: Annotated[str, Query(alias="leagueName")],
    currency_one_item_id: Annotated[int, Query(alias="currencyOneItemId")],
    currency_two_item_id: Annotated[int, Query(alias="currencyTwoItemId")],
    limit: int,
    end_epoch: int | None = None
) -> GetPairHistoryRequest:
    return GetPairHistoryRequest(
        league_name=league_name,
        currency_one_item_id=currency_one_item_id,
        currency_two_item_id=currency_two_item_id,
        limit=limit,
        end_epoch=end_epoch
    )

GetPairHistoryRequestDep = Annotated[
    GetPairHistoryRequest,
    get_pair_history_request
]

class GetPairHistoryResponse(BaseModel):
    class _Pair(BaseModel):
        class _Data(BaseModel):
            class _Details(BaseModel):
                currency_item_id: int
                value_traded: Decimal
                relative_price: Decimal
                stock_value: Decimal
                volume_traded: int
                highest_stock: int

                @classmethod
                def from_model(cls, model: PairDataDetails) -> Self:
                    return cls(
                        currency_item_id=model.CurrencyItemId,
                        value_traded=model.ValueTraded,
                        relative_price=model.RelativePrice,
                        stock_value=model.StockValue,
                        volume_traded=model.VolumeTraded,
                        highest_stock=model.HighestStock,
                    )

            currency_one_data: _Details
            currency_two_data: _Details

            @classmethod
            def from_model(cls, model: PairData) -> Self:
                return cls(
                    currency_one_data=cls._Details.from_model(model.CurrencyOneData),
                    currency_two_data=cls._Details.from_model(model.CurrencyTwoData)
                )
            
        epoch: int
        data: _Data

        @classmethod
        def from_model(cls, model: GetCurrentSnapshotPairModel) -> Self:
            return cls(
                epoch=model.Epoch,
                data=cls._Data.from_model(model.Data)
            )

    history: list[_Pair]
    meta: dict[str, object]

    @classmethod
    def from_model(cls, model: GetPairHistoryModel) -> Self:
        return cls(
            history=[cls._Pair.from_model(history) for history in model.History],
            meta=model.Meta
        )


@router.get("/PairHistory")
async def get_pair_history(
    request: GetPairHistoryRequestDep,
    item_repository: ItemRepoDep,
    currency_exchange_repository: CXRepoDep,
) -> GetPairHistoryModel:
    league = await item_repository.GetLeagueByValue(request.league_name)

    if not league:
        raise HTTPException(400, "Invalid league name")

    getCurrencyExchangeResponse = await currency_exchange_repository.GetPairHistory(
        request.currency_one_item_id,
        request.currency_two_item_id,
        league.id,
        request.end_epoch if request.end_epoch else int(datetime.now(tz=timezone.utc).timestamp()),
        request.limit,
    )

    if not getCurrencyExchangeResponse:
        raise HTTPException(404, "No data for given league.")

    return getCurrencyExchangeResponse
