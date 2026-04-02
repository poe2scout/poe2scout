
from datetime import datetime
from decimal import Decimal
from typing import Annotated, List, Self

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel

from poe2scout.api.dependancies import ItemRepoDep
from poe2scout.db.repositories.item_repository.GetAllItemHistories import (
    ItemHistory,
    ItemHistoryLog,
)
from . import router

class GetAllItemHistoriesResponse(BaseModel):
    class _ItemHistory(BaseModel):
        class _ItemHistoryLog(BaseModel):
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
        history: List[_ItemHistoryLog]

        @classmethod
        def from_model(cls, item_history: ItemHistory) -> Self:
            return cls(
                item_id=item_history.ItemId,
                history=[
                    cls._ItemHistoryLog.from_model(log) 
                    for log in item_history.History
                ],
            )

    item_histories: List[_ItemHistory]

    @classmethod
    def from_model(cls, item_histories: List[ItemHistory]) -> Self:
        return cls(
            item_histories=[
                cls._ItemHistory.from_model(item_history) 
                for item_history in item_histories
            ],
        )
    
class GetItemHistoriesRequest(BaseModel):
    league_name: str

def get_item_histories_request(
    league_name: Annotated[str, Query(alias="leagueName")]
)-> GetItemHistoriesRequest:
    return GetItemHistoriesRequest(
        league_name=league_name
    )

GetItemHistoryRequestDep = Annotated[
    GetItemHistoriesRequest,
    Depends(get_item_histories_request),
]

@router.get("/History")
async def get_item_histories(
    request: GetItemHistoryRequestDep,
    item_repository: ItemRepoDep
) -> GetAllItemHistoriesResponse:
    league = await item_repository.GetLeagueByValue(request.league_name)

    if not league:
        raise HTTPException(400, "Invalid league name")

    item_histories = await item_repository.GetAllItemHistories(league.id)

    return GetAllItemHistoriesResponse.from_model(item_histories)
