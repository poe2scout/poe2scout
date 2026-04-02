from decimal import Decimal
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Query

from poe2scout.api.dependancies import CXRepoDep, ItemRepoDep, cache_response
from poe2scout.api.models import ApiModel
from poe2scout.db.repositories.currency_exchange_repository.GetCurrentSnapshotPairs import (
    GetCurrentSnapshotPairModel,
    PairDataDetails,
)
from poe2scout.db.repositories.models import CurrencyItem

from . import router


class GetSnapshotPairsRequest(ApiModel):
    league_name: str


def get_snapshot_pairs_request(
    league_name: Annotated[str, Query(alias="LeagueName")],
) -> GetSnapshotPairsRequest:
    return GetSnapshotPairsRequest(league_name=league_name)


GetSnapshotPairsRequestDep = Annotated[
    GetSnapshotPairsRequest,
    Depends(get_snapshot_pairs_request),
]


class GetSnapshotPairsResponse(ApiModel):
    class _CurrencyItem(ApiModel):
        id: int
        item_id: int
        currency_category_id: int
        api_id: str
        text: str
        category_api_id: str
        icon_url: str | None = None
        item_metadata: dict | None = None

        @classmethod
        def from_model(cls, model: CurrencyItem) -> Self:
            return cls(
                id=model.id,
                item_id=model.itemId,
                currency_category_id=model.currencyCategoryId,
                api_id=model.apiId,
                text=model.text,
                category_api_id=model.categoryApiId,
                icon_url=model.iconUrl,
                item_metadata=model.itemMetadata,
            )

    class _PairData(ApiModel):
        value_traded: Decimal
        relative_price: Decimal
        stock_value: Decimal
        volume_traded: int
        highest_stock: int

        @classmethod
        def from_model(cls, model: PairDataDetails) -> Self:
            return cls(
                value_traded=model.ValueTraded,
                relative_price=model.RelativePrice,
                stock_value=model.StockValue,
                volume_traded=model.VolumeTraded,
                highest_stock=model.HighestStock,
            )

    volume: Decimal
    currency_one: _CurrencyItem
    currency_two: _CurrencyItem
    currency_one_data: _PairData
    currency_two_data: _PairData

    @classmethod
    def from_model(cls, model: GetCurrentSnapshotPairModel) -> Self:
        return cls(
            volume=model.Volume,
            currency_one=cls._CurrencyItem.from_model(model.CurrencyOne),
            currency_two=cls._CurrencyItem.from_model(model.CurrencyTwo),
            currency_one_data=cls._PairData.from_model(model.CurrencyOneData),
            currency_two_data=cls._PairData.from_model(model.CurrencyTwoData),
        )


@router.get("/SnapshotPairs")
@cache_response(
    key=lambda params: f"snapshot_pairs:{params['request'].league_name}",
    ttl=60 * 10,
)
async def get_snapshot_pairs(
    request: GetSnapshotPairsRequestDep,
    item_repository: ItemRepoDep,
    currency_exchange_repository: CXRepoDep,
) -> list[GetSnapshotPairsResponse]:
    league = await item_repository.GetLeagueByValue(request.league_name)

    if league is None:
        raise HTTPException(400, "Invalid league name")

    snapshot_pairs = await currency_exchange_repository.GetCurrentSnapshotPairs(league.id)
    return [GetSnapshotPairsResponse.from_model(pair) for pair in snapshot_pairs]
