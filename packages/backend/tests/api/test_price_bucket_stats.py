from datetime import datetime
import unittest
from unittest.mock import patch

from poe2scout.db.repositories.price_log_repository.get_item_price_bucket_stats import (
    GetItemPriceBucketStatsDto,
    get_item_price_bucket_stats,
)


class FakeCursor:
    def __init__(self, rows: list[GetItemPriceBucketStatsDto]):
        self.rows = rows
        self.query: str | None = None
        self.params: dict[str, object] | None = None

    async def execute(self, query: str, params: dict[str, object]) -> None:
        self.query = query
        self.params = params

    async def fetchall(self) -> list[GetItemPriceBucketStatsDto]:
        return self.rows


class FakeCursorContext:
    def __init__(self, cursor: FakeCursor):
        self.cursor = cursor

    async def __aenter__(self) -> FakeCursor:
        return self.cursor

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None


class PriceBucketStatsRepositoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_bucket_stats_uses_average_price_and_summed_quantity(self):
        bucket_starts = [
            datetime(2026, 6, 12, 12),
            datetime(2026, 6, 12, 6),
        ]
        cursor = FakeCursor(
            [
                GetItemPriceBucketStatsDto(
                    item_id=10,
                    block_index=0,
                    price=12.5,
                    quantity=42,
                    time=bucket_starts[0],
                ),
                GetItemPriceBucketStatsDto(
                    item_id=10,
                    block_index=1,
                    price=None,
                    quantity=None,
                    time=bucket_starts[1],
                ),
            ]
        )

        with patch(
            "poe2scout.db.repositories.price_log_repository.get_item_price_bucket_stats."
            "BaseRepository.get_db_cursor",
            return_value=FakeCursorContext(cursor),
        ):
            price_logs = await get_item_price_bucket_stats(
                item_ids=[10],
                league_id=7,
                realm_id=4,
                bucket_starts=bucket_starts,
                frequency_hours=6,
            )

        self.assertIn("avg(pl.price)", cursor.query)
        self.assertIn("sum(pl.quantity)", cursor.query)
        self.assertEqual(cursor.params["block_starts"], bucket_starts)
        self.assertEqual(cursor.params["block_indices"], [0, 1])
        self.assertEqual(cursor.params["frequency_hours"], 6)
        self.assertEqual(price_logs[10][0].price, 12.5)
        self.assertEqual(price_logs[10][0].quantity, 42)
        self.assertIsNone(price_logs[10][1])


if __name__ == "__main__":
    unittest.main()
