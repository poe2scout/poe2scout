import unittest
from datetime import date
from unittest.mock import AsyncMock, patch

from poe2scout.api.economy_cache import (
    CacheKey,
    EconomyCache,
    build_daily_stat_price_logs,
)
from poe2scout.db.repositories.price_log_repository.get_item_daily_stats import (
    GetItemDailyStatsDto,
)


class EconomyCacheTests(unittest.IsolatedAsyncioTestCase):
    async def test_build_daily_stat_price_logs_uses_volume_as_quantity(self):
        stats = [
            GetItemDailyStatsDto(
                item_id=10,
                avg_price=12.5,
                data_points=3,
                volume=42,
                day=date(2026, 4, 25),
            )
        ]

        price_logs = build_daily_stat_price_logs(
            [10],
            [date(2026, 4, 25)],
            stats,
        )

        self.assertIsNotNone(price_logs[10][0])
        self.assertEqual(price_logs[10][0].price, 12.5)
        self.assertEqual(price_logs[10][0].quantity, 42)

    async def test_fetch_unique_page_skips_price_queries_when_category_has_no_league_items(self):
        cache = EconomyCache()
        cache_key = CacheKey(
            category="body_armour",
            league_id=999,
            realm_id=1,
            game_id=1,
            reference_currency="",
        )

        with (
            patch(
                "poe2scout.api.economy_cache.league_repository.get_items_in_current_league",
                AsyncMock(return_value=[]),
            ),
            patch(
                "poe2scout.api.economy_cache.unique_item_repository.get_unique_items_by_category",
                AsyncMock(return_value=[]),
            ),
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_price_logs",
                AsyncMock(),
            ) as get_item_price_logs,
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_prices",
                AsyncMock(),
            ) as get_item_prices,
        ):
            items = await cache.fetch_unique_page(cache_key)

        self.assertEqual(items, [])
        get_item_price_logs.assert_not_awaited()
        get_item_prices.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
