import unittest
from unittest.mock import AsyncMock, patch

from poe2scout.api.economy_cache import CacheKey, EconomyCache


class EconomyCacheTests(unittest.IsolatedAsyncioTestCase):
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
