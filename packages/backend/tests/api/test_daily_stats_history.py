from datetime import date
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from poe2scout.api.routes.leagues.items.get_daily_stats_history import (
    GetDailyStatsHistoryRequest,
    get_daily_stats_history,
)
from poe2scout.db.repositories.league_repository.get_leagues import League
from poe2scout.db.repositories.price_log_repository.get_item_daily_stats_history import (
    DailyStatsHistoryEntry,
    GetItemDailyStatsHistoryModel,
    get_item_daily_stats_history,
)
from poe2scout.db.repositories.realm_repository.get_realm import Realm


class FakeCursor:
    def __init__(self, rows: list[DailyStatsHistoryEntry]):
        self.rows = rows
        self.query: str | None = None
        self.params: dict[str, object] | None = None

    async def execute(self, query: str, params: dict[str, object]) -> None:
        self.query = query
        self.params = params

    async def fetchall(self) -> list[DailyStatsHistoryEntry]:
        return self.rows


class FakeCursorContext:
    def __init__(self, cursor: FakeCursor):
        self.cursor = cursor

    async def __aenter__(self) -> FakeCursor:
        return self.cursor

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None


def make_daily_stat(day: date, close_price: float) -> DailyStatsHistoryEntry:
    return DailyStatsHistoryEntry(
        day=day,
        open_price=close_price - 1,
        close_price=close_price,
        min_price=close_price - 2,
        max_price=close_price + 2,
        avg_price=close_price + 0.5,
    )


def make_league() -> League:
    return League(
        league_id=7,
        value="Standard",
        base_currency_item_id=10,
        base_currency_api_id="exalted",
        base_currency_text="Exalted Orb",
    )


class DailyStatsHistoryRepositoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_end_date_returns_latest_page_newest_to_oldest(self):
        cursor = FakeCursor(
            [
                make_daily_stat(date(2026, 4, 25), 30),
                make_daily_stat(date(2026, 4, 24), 20),
                make_daily_stat(date(2026, 4, 23), 10),
            ]
        )

        with patch(
            "poe2scout.db.repositories.price_log_repository."
            "get_item_daily_stats_history.BaseRepository.get_db_cursor",
            return_value=FakeCursorContext(cursor),
        ):
            history = await get_item_daily_stats_history(
                item_id=100,
                league_id=7,
                realm_id=2,
                day_count=2,
                end_date=None,
            )

        self.assertTrue(history.has_more)
        self.assertEqual([stat.day for stat in history.daily_stats], [
            date(2026, 4, 25),
            date(2026, 4, 24),
        ])
        self.assertEqual(cursor.params["end_date"], None)
        self.assertEqual(cursor.params["limit"], 3)

    async def test_end_date_is_passed_as_exclusive_cursor(self):
        cursor = FakeCursor([make_daily_stat(date(2026, 4, 23), 10)])
        end_date = date(2026, 4, 24)

        with patch(
            "poe2scout.db.repositories.price_log_repository."
            "get_item_daily_stats_history.BaseRepository.get_db_cursor",
            return_value=FakeCursorContext(cursor),
        ):
            history = await get_item_daily_stats_history(
                item_id=100,
                league_id=7,
                realm_id=2,
                day_count=2,
                end_date=end_date,
            )

        self.assertFalse(history.has_more)
        self.assertIn("day < %(end_date)s::date", cursor.query)
        self.assertEqual(cursor.params["end_date"], end_date)
        self.assertEqual([stat.day for stat in history.daily_stats], [date(2026, 4, 23)])


class DailyStatsHistoryRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_route_maps_daily_stats_and_base_currency_metadata(self):
        request = GetDailyStatsHistoryRequest(
            realm="poe2",
            item_id=100,
            league_name="Standard",
            day_count=2,
            end_date=None,
        )
        history = GetItemDailyStatsHistoryModel(
            daily_stats=[
                make_daily_stat(date(2026, 4, 25), 30),
                make_daily_stat(date(2026, 4, 24), 20),
            ],
            has_more=False,
        )

        with (
            patch(
                "poe2scout.api.routes.leagues.items.get_daily_stats_history."
                "realm_repository.get_realm",
                AsyncMock(return_value=Realm(realm_id=2, game_id=3)),
            ),
            patch(
                "poe2scout.api.routes.leagues.items.get_daily_stats_history."
                "league_repository.get_league_by_value",
                AsyncMock(return_value=make_league()),
            ),
            patch(
                "poe2scout.api.routes.leagues.items.get_daily_stats_history."
                "price_log_repository.get_item_daily_stats_history",
                AsyncMock(return_value=history),
            ) as get_history,
        ):
            response = await get_daily_stats_history(request)

        get_history.assert_awaited_once_with(100, 7, 2, 2, None)
        self.assertFalse(response.has_more)
        self.assertEqual(response.base_currency_api_id, "exalted")
        self.assertEqual(response.base_currency_text, "Exalted Orb")
        self.assertEqual([stat.time for stat in response.daily_stats], [
            date(2026, 4, 24),
            date(2026, 4, 25),
        ])
        self.assertEqual(response.daily_stats[1].open, 29)
        self.assertEqual(response.daily_stats[1].high, 32)
        self.assertEqual(response.daily_stats[1].low, 28)
        self.assertEqual(response.daily_stats[1].close, 30)
        self.assertEqual(response.daily_stats[1].average, 30.5)

    async def test_route_rejects_non_positive_day_count(self):
        request = GetDailyStatsHistoryRequest(
            realm="poe2",
            item_id=100,
            league_name="Standard",
            day_count=0,
            end_date=None,
        )

        with self.assertRaises(HTTPException) as raised:
            await get_daily_stats_history(request)

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(raised.exception.detail, "DayCount must be positive")

    async def test_route_rejects_invalid_realm(self):
        request = GetDailyStatsHistoryRequest(
            realm="unknown",
            item_id=100,
            league_name="Standard",
            day_count=2,
            end_date=None,
        )

        with (
            patch(
                "poe2scout.api.routes.leagues.items.get_daily_stats_history."
                "realm_repository.get_realm",
                AsyncMock(return_value=None),
            ),
            self.assertRaises(HTTPException) as raised,
        ):
            await get_daily_stats_history(request)

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(raised.exception.detail, "Invalid realm")

    async def test_route_rejects_invalid_league(self):
        request = GetDailyStatsHistoryRequest(
            realm="poe2",
            item_id=100,
            league_name="Unknown",
            day_count=2,
            end_date=None,
        )

        with (
            patch(
                "poe2scout.api.routes.leagues.items.get_daily_stats_history."
                "realm_repository.get_realm",
                AsyncMock(return_value=Realm(realm_id=2, game_id=3)),
            ),
            patch(
                "poe2scout.api.routes.leagues.items.get_daily_stats_history."
                "league_repository.get_league_by_value",
                AsyncMock(return_value=None),
            ),
            self.assertRaises(HTTPException) as raised,
        ):
            await get_daily_stats_history(request)

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(raised.exception.detail, "League does not exist")


if __name__ == "__main__":
    unittest.main()
