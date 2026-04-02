from datetime import datetime
from decimal import Decimal
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Query

from poe2scout.api.dependancies import ItemRepoDep
from poe2scout.api.models import ApiModel
from poe2scout.db.repositories.item_repository.GetAllItemHistories import (
    ItemHistory,
    ItemHistoryLog,
)

from . import router


class GetAllItemHistoriesResponse(ApiModel):
    class _ItemHistory(ApiModel):
        class _ItemHistoryLog(ApiModel):
            price: Decimal
            time: datetime
            quantity: int

            @classmethod
            def from_model(cls, log: ItemHistoryLog) -> Self:
                return cls(
                    price=log.Price,
                    time=log.Time,
                    quantity=log.Quantity,
                )

        item_id: int
        history: list[_ItemHistoryLog]

        @classmethod
        def from_model(cls, item_history: ItemHistory) -> Self:
            return cls(
                item_id=item_history.ItemId,
                history=[
                    cls._ItemHistoryLog.from_model(log) for log in item_history.History
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


class GetItemHistoriesRequest(ApiModel):
    league_name: str


def get_item_histories_request(
    league_name: Annotated[str, Query(alias="LeagueName")],
) -> GetItemHistoriesRequest:
    return GetItemHistoriesRequest(league_name=league_name)


GetItemHistoryRequestDep = Annotated[
    GetItemHistoriesRequest,
    Depends(get_item_histories_request),
]


@router.get("/History")
async def get_item_histories(
    request: GetItemHistoryRequestDep,
    item_repository: ItemRepoDep,
) -> GetAllItemHistoriesResponse:
    league = await item_repository.GetLeagueByValue(request.league_name)

    if league is None:
        raise HTTPException(400, "Invalid league name")

    item_histories = await item_repository.GetAllItemHistories(league.id)

    return GetAllItemHistoriesResponse.from_model(item_histories)
