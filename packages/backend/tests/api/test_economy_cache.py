import unittest
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from poe2scout.api.economy_cache import (
    CacheKey,
    EconomyCache,
    build_daily_stat_price_logs,
    get_price_history_bucket_starts,
)
from poe2scout.api.history_config import (
    get_category_price_history_config,
)
from poe2scout.db.repositories.models import CurrencyItem, PriceLogEntry
from poe2scout.db.repositories.price_log_repository.get_item_daily_stats import (
    GetItemDailyStatsDto,
)
from poe2scout.db.repositories.price_log_repository.get_item_prices import (
    GetItemPricesModel,
)
from poe2scout.db.repositories.unique_item_repository.get_all_unique_items import UniqueItem


class EconomyCacheTests(unittest.IsolatedAsyncioTestCase):
    async def test_history_config_defaults_to_daily_seven_point_history(self):
        history_config = get_category_price_history_config()

        self.assertEqual(history_config.data_points, 7)
        self.assertEqual(history_config.frequency_hours, 24)

    async def test_history_config_rejects_invalid_data_points(self):
        with self.assertRaises(HTTPException) as raised:
            get_category_price_history_config(data_points=6)

        self.assertEqual(raised.exception.status_code, 400)

    async def test_history_config_rejects_invalid_frequency(self):
        with self.assertRaises(HTTPException) as raised:
            get_category_price_history_config(frequency_hours=5)

        self.assertEqual(raised.exception.status_code, 400)

    async def test_bucket_starts_use_static_utc_frequency_boundaries(self):
        bucket_starts = get_price_history_bucket_starts(
            data_points=8,
            frequency_hours=6,
            time_utc=datetime(2026, 6, 12, 17, 45, tzinfo=timezone.utc),
        )

        self.assertEqual(
            bucket_starts[:4],
            [
                datetime(2026, 6, 12, 12),
                datetime(2026, 6, 12, 6),
                datetime(2026, 6, 12, 0),
                datetime(2026, 6, 11, 18),
            ],
        )
        self.assertEqual(len(bucket_starts), 8)

    async def test_cache_keys_include_history_config(self):
        daily_key = CacheKey(
            category="currency",
            league_id=7,
            realm_id=1,
            game_id=1,
            reference_currency="exalted",
            data_points=7,
            frequency_hours=24,
        )
        bucket_key = CacheKey(
            category="currency",
            league_id=7,
            realm_id=1,
            game_id=1,
            reference_currency="exalted",
            data_points=8,
            frequency_hours=6,
        )

        self.assertNotEqual(daily_key, bucket_key)

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

    async def test_get_category_price_logs_uses_daily_stats_for_24_hour_frequency(self):
        cache = EconomyCache()
        cache_key = CacheKey(
            category="currency",
            league_id=7,
            realm_id=1,
            game_id=1,
            reference_currency="",
            data_points=7,
            frequency_hours=24,
        )
        daily_stat = GetItemDailyStatsDto(
            item_id=10,
            avg_price=12.5,
            data_points=3,
            volume=42,
            day=date.today(),
        )

        with (
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_daily_stats",
                AsyncMock(return_value=[daily_stat]),
            ) as get_item_daily_stats,
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_price_bucket_stats",
                AsyncMock(),
            ) as get_item_price_bucket_stats,
        ):
            price_logs = await cache.get_category_price_logs(
                [10],
                cache_key.league_id,
                cache_key.realm_id,
                data_points=7,
                frequency_hours=24,
                time_utc=datetime(2026, 6, 12, 17, 45, tzinfo=timezone.utc),
            )

        get_item_daily_stats.assert_awaited_once()
        get_item_price_bucket_stats.assert_not_awaited()
        self.assertEqual(len(price_logs[10]), 7)

    async def test_get_category_price_logs_uses_bucket_stats_for_subday_frequency(self):
        cache = EconomyCache()
        cache_key = CacheKey(
            category="currency",
            league_id=7,
            realm_id=1,
            game_id=1,
            reference_currency="",
            data_points=8,
            frequency_hours=6,
        )
        bucket_logs = {10: [None] * 8}

        with (
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_daily_stats",
                AsyncMock(),
            ) as get_item_daily_stats,
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_price_bucket_stats",
                AsyncMock(return_value=bucket_logs),
            ) as get_item_price_bucket_stats,
        ):
            price_logs = await cache.get_category_price_logs(
                [10],
                cache_key.league_id,
                cache_key.realm_id,
                data_points=8,
                frequency_hours=6,
                time_utc=datetime(2026, 6, 12, 17, 45, tzinfo=timezone.utc),
            )

        get_item_daily_stats.assert_not_awaited()
        get_item_price_bucket_stats.assert_awaited_once()
        self.assertEqual(price_logs[10], [None] * 8)

    async def test_fetch_unique_page_uses_latest_raw_quantity_for_current_quantity(self):
        cache = EconomyCache()
        cache_key = CacheKey(
            category="currency",
            league_id=7,
            realm_id=1,
            game_id=1,
            reference_currency="",
            data_points=7,
            frequency_hours=24,
        )
        unique_item = UniqueItem(
            unique_item_id=100,
            item_id=10,
            icon_url=None,
            text="Mirror of Kalandra",
            name="Mirror of Kalandra",
            category_api_id="currency",
            item_metadata=None,
            type="Currency",
            is_chanceable=False,
            is_current=True,
        )
        daily_stat = GetItemDailyStatsDto(
            item_id=10,
            avg_price=12.5,
            data_points=3,
            volume=42,
            day=date.today(),
        )
        latest_price = GetItemPricesModel(item_id=10, price=5.0, quantity=102)

        with (
            patch(
                "poe2scout.api.economy_cache.league_repository.get_items_in_current_league",
                AsyncMock(return_value=[10]),
            ),
            patch(
                "poe2scout.api.economy_cache.unique_item_repository.get_unique_items_by_category",
                AsyncMock(return_value=[unique_item]),
            ),
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_daily_stats",
                AsyncMock(return_value=[daily_stat]),
            ),
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_prices",
                AsyncMock(return_value=[latest_price]),
            ),
        ):
            items = await cache.fetch_unique_page(cache_key)

        self.assertEqual(items[0].price_logs[0].price, 12.5)
        self.assertEqual(items[0].price_logs[0].quantity, 42)
        self.assertEqual(items[0].current_price, 5.0)
        self.assertEqual(items[0].current_quantity, 102)

    async def test_fetch_unique_page_skips_price_queries_when_category_has_no_league_items(self):
        cache = EconomyCache()
        cache_key = CacheKey(
            category="body_armour",
            league_id=999,
            realm_id=1,
            game_id=1,
            reference_currency="",
            data_points=7,
            frequency_hours=24,
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

    async def test_fetch_unique_page_converts_bucket_logs_with_reference_currency(self):
        cache = EconomyCache()
        cache_key = CacheKey(
            category="currency",
            league_id=7,
            realm_id=1,
            game_id=1,
            reference_currency="divine",
            data_points=8,
            frequency_hours=6,
        )
        unique_item = UniqueItem(
            unique_item_id=100,
            item_id=10,
            icon_url=None,
            text="Mirror of Kalandra",
            name="Mirror of Kalandra",
            category_api_id="currency",
            item_metadata=None,
            type="Currency",
            is_chanceable=False,
            is_current=True,
        )
        reference_currency = CurrencyItem(
            currency_item_id=200,
            item_id=99,
            currency_category_id=2,
            api_id="divine",
            text="Divine Orb",
            category_api_id="currency",
            icon_url=None,
            item_metadata=None,
        )
        bucket_time = datetime(2026, 6, 12, 12)
        item_logs = {10: [PriceLogEntry(price=10, time=bucket_time, quantity=5)] + [None] * 7}
        reference_logs = {99: [PriceLogEntry(price=2, time=bucket_time, quantity=20)] + [None] * 7}
        latest_price = GetItemPricesModel(item_id=10, price=20.0, quantity=102)

        async def get_bucket_stats(item_ids, *args):
            if item_ids == [10]:
                return item_logs

            return reference_logs

        with (
            patch(
                "poe2scout.api.economy_cache.league_repository.get_items_in_current_league",
                AsyncMock(return_value=[10]),
            ),
            patch(
                "poe2scout.api.economy_cache.unique_item_repository.get_unique_items_by_category",
                AsyncMock(return_value=[unique_item]),
            ),
            patch(
                "poe2scout.api.economy_cache.currency_item_repository.get_currency_item",
                AsyncMock(return_value=reference_currency),
            ),
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_price",
                AsyncMock(return_value=2.0),
            ),
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_price_bucket_stats",
                AsyncMock(side_effect=get_bucket_stats),
            ) as get_item_price_bucket_stats,
            patch(
                "poe2scout.api.economy_cache.price_log_repository.get_item_prices",
                AsyncMock(return_value=[latest_price]),
            ),
        ):
            items = await cache.fetch_unique_page(cache_key)

        self.assertEqual(get_item_price_bucket_stats.await_count, 2)
        self.assertEqual(items[0].price_logs[0].price, 5.0)
        self.assertEqual(items[0].current_price, 10.0)


if __name__ == "__main__":
    unittest.main()
