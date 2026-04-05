from decimal import Decimal
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path

from poe2scout.api.dependancies import CXRepoDep, LeagueRepoDep, cache_response
from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories.currency_exchange_repository.get_current_snapshot_pairs import (
    GetCurrentSnapshotPairModel,
    PairDataDetails,
)
from poe2scout.db.repositories.models import CurrencyItem

from . import router


class GetSnapshotPairsRequest(ApiModel):
    league_name: str


def get_snapshot_pairs_request(
    league_name: Annotated[str, Path(alias="LeagueName")],
) -> GetSnapshotPairsRequest:
    return GetSnapshotPairsRequest(league_name=league_name)


GetSnapshotPairsRequestDep = Annotated[
    GetSnapshotPairsRequest,
    Depends(get_snapshot_pairs_request),
]


class GetSnapshotPairsResponse(ApiModel):
    class _CurrencyItem(ApiModel):
        currency_item_id: int
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
                currency_item_id=model.currency_item_id,
                item_id=model.item_id,
                currency_category_id=model.currency_category_id,
                api_id=model.api_id,
                text=model.text,
                category_api_id=model.category_api_id,
                icon_url=model.icon_url,
                item_metadata=model.item_metadata,
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
                value_traded=model.value_traded,
                relative_price=model.relative_price,
                stock_value=model.stock_value,
                volume_traded=model.volume_traded,
                highest_stock=model.highest_stock,
            )
    currency_exchange_snapshot_pair_id: int
    currency_exchange_snapshot_id: int
    volume: Decimal
    currency_one: _CurrencyItem
    currency_two: _CurrencyItem
    currency_one_data: _PairData
    currency_two_data: _PairData

    @classmethod
    def from_model(cls, model: GetCurrentSnapshotPairModel) -> Self:
        return cls(
            currency_exchange_snapshot_pair_id=model.currency_exchange_snapshot_pair_id,
            currency_exchange_snapshot_id=model.currency_exchange_snapshot_id,
            volume=model.volume,
            currency_one=cls._CurrencyItem.from_model(model.currency_one),
            currency_two=cls._CurrencyItem.from_model(model.currency_two),
            currency_one_data=cls._PairData.from_model(model.currency_one_data),
            currency_two_data=cls._PairData.from_model(model.currency_two_data),
        )


@router.get("/{LeagueName}/SnapshotPairs")
@cache_response(
    key=lambda params: f"snapshot_pairs:{params['request'].league_name}",
    ttl=60 * 10,
)
async def get_snapshot_pairs(
    request: GetSnapshotPairsRequestDep,
    currency_exchange_repository: CXRepoDep,
    league_repository: LeagueRepoDep
) -> list[GetSnapshotPairsResponse]:
    league = await league_repository.get_league_by_value(request.league_name)

    if league is None:
        raise HTTPException(400, "Invalid league name")

    snapshot_pairs = await currency_exchange_repository.get_current_snapshot_pairs(
        league.league_id
    )
    return [GetSnapshotPairsResponse.from_model(pair) for pair in snapshot_pairs]
