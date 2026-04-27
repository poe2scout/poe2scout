from datetime import date
from typing import Annotated, Self

from fastapi import Depends, HTTPException, Path, Query

from poe2scout.api.api_model import ApiModel
from poe2scout.db.repositories import league_repository, price_log_repository, realm_repository
from poe2scout.db.repositories.price_log_repository.get_item_daily_stats_history import (
    DailyStatsHistoryEntry,
)

from .. import router


class GetDailyStatsHistoryRequest(ApiModel):
    realm: str
    item_id: int
    league_name: str
    day_count: int
    end_date: date | None


def get_daily_stats_history_request(
    realm: Annotated[str, Path(alias="Realm")],
    league_name: Annotated[str, Path(alias="LeagueName")],
    item_id: Annotated[int, Path(alias="ItemId")],
    day_count: Annotated[int, Query(alias="DayCount")],
    end_date: Annotated[date | None, Query(alias="EndDate")] = None,
) -> GetDailyStatsHistoryRequest:
    return GetDailyStatsHistoryRequest(
        realm=realm,
        item_id=item_id,
        league_name=league_name,
        day_count=day_count,
        end_date=end_date,
    )


GetDailyStatsHistoryRequestDep = Annotated[
    GetDailyStatsHistoryRequest,
    Depends(get_daily_stats_history_request),
]


class GetDailyStatsHistoryResponse(ApiModel):
    class _DailyStatsPoint(ApiModel):
        time: date
        open: float
        high: float
        low: float
        close: float
        average: float
        volume: int

        @classmethod
        def from_model(cls, daily_stats: DailyStatsHistoryEntry) -> Self:
            return cls(
                time=daily_stats.day,
                open=daily_stats.open_price,
                high=daily_stats.max_price,
                low=daily_stats.min_price,
                close=daily_stats.close_price,
                average=daily_stats.avg_price,
                volume=daily_stats.volume,
            )

    daily_stats: list[_DailyStatsPoint]
    has_more: bool
    base_currency_api_id: str
    base_currency_text: str

    @classmethod
    def from_model(
        cls,
        daily_stats_history: list[DailyStatsHistoryEntry],
        has_more: bool,
        base_currency_api_id: str,
        base_currency_text: str,
    ) -> Self:
        return cls(
            daily_stats=[
                cls._DailyStatsPoint.from_model(daily_stats)
                for daily_stats in reversed(daily_stats_history)
            ],
            has_more=has_more,
            base_currency_api_id=base_currency_api_id,
            base_currency_text=base_currency_text,
        )


@router.get("/{LeagueName}/Items/{ItemId}/DailyStatsHistory")
async def get_daily_stats_history(
    request: GetDailyStatsHistoryRequestDep,
) -> GetDailyStatsHistoryResponse:
    if request.day_count <= 0:
        raise HTTPException(400, "DayCount must be positive")

    realm = await realm_repository.get_realm(request.realm)

    if realm is None:
        raise HTTPException(400, "Invalid realm")

    league = await league_repository.get_league_by_value(request.league_name, realm.game_id)

    if league is None:
        raise HTTPException(400, "League does not exist")

    daily_stats_history = await price_log_repository.get_item_daily_stats_history(
        request.item_id,
        league.league_id,
        realm.realm_id,
        request.day_count + 1,
        request.end_date,
    )
    has_more = len(daily_stats_history) > request.day_count

    if has_more:
        daily_stats_history = daily_stats_history[: request.day_count]

    return GetDailyStatsHistoryResponse.from_model(
        daily_stats_history,
        has_more=has_more,
        base_currency_api_id=league.base_currency_api_id,
        base_currency_text=league.base_currency_text,
    )
