from datetime import datetime
from decimal import Decimal
from typing import Annotated, Self

from fastapi import Depends, Path

from poe2scout.api.api_model import ApiModel
from poe2scout.api.dependancies import LeagueContextDep
from poe2scout.db.repositories import price_log_repository
from poe2scout.db.repositories.price_log_repository.get_all_item_histories import (
    ItemHistory,
    ItemHistoryLog,
)

from . import router


class GetItemPriceHistoriesResponse(ApiModel):
    class _ItemHistory(ApiModel):
        class _ItemHistoryLog(ApiModel):
            price: Decimal
            time: datetime
            quantity: int

            @classmethod
            def from_model(cls, log: ItemHistoryLog) -> Self:
                return cls(
                    price=log.price,
                    time=log.time,
                    quantity=log.quantity,
                )

        item_id: int
        history: list[_ItemHistoryLog]

        @classmethod
        def from_model(cls, item_history: ItemHistory) -> Self:
            return cls(
                item_id=item_history.item_id,
                history=[
                    cls._ItemHistoryLog.from_model(log) for log in item_history.history
                ],
            )

    item_histories: list[_ItemHistory]

    @classmethod
    def from_model(cls, item_histories: list[ItemHistory]) -> Self:
        return cls(
            item_histories=[
                cls._ItemHistory.from_model(item_history)
                for item_history in item_histories
            ],
        )


class GetItemPriceHistoriesRequest(ApiModel):
    realm: str
    league_name: str


def get_item_price_histories_request(
    realm: Annotated[str, Path(alias="Realm")],
    league_name: Annotated[str, Path(alias="LeagueName")],
) -> GetItemPriceHistoriesRequest:
    return GetItemPriceHistoriesRequest(realm=realm, league_name=league_name)


GetItemPriceHistoryRequestDep = Annotated[
    GetItemPriceHistoriesRequest,
    Depends(get_item_price_histories_request),
]


@router.get("/PriceHistory")
async def get_item_price_histories(
    request: GetItemPriceHistoryRequestDep,
    context: LeagueContextDep,
) -> GetItemPriceHistoriesResponse:
    realm = context.realm
    league = context.league

    item_histories = await price_log_repository.get_all_item_histories(
        league.league_id, 
        realm.realm_id
    )

    return GetItemPriceHistoriesResponse.from_model(item_histories)
