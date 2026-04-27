import unittest
from unittest.mock import patch

from poe2scout.db.repositories.price_log_repository.record_price import (
    RecordPriceModel,
    record_price,
    record_price_bulk,
)


class FakeCursor:
    def __init__(self):
        self.query: str | None = None
        self.params: dict[str, object] | None = None

    async def execute(self, query: str, params: dict[str, object]) -> None:
        self.query = query
        self.params = params


class FakeCursorContext:
    def __init__(self, cursor: FakeCursor):
        self.cursor = cursor

    async def __aenter__(self) -> FakeCursor:
        return self.cursor

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None


class RecordPriceDailyStatsTests(unittest.IsolatedAsyncioTestCase):
    async def test_record_price_writes_quantity_to_daily_volume(self):
        cursor = FakeCursor()

        with patch(
            "poe2scout.db.repositories.price_log_repository."
            "record_price.BaseRepository.get_db_cursor",
            return_value=FakeCursorContext(cursor),
        ):
            await record_price(
                RecordPriceModel(
                    item_id=10,
                    league_id=20,
                    realm_id=30,
                    price=4.5,
                    quantity=7,
                )
            )

        self.assertIn("quantity AS volume", cursor.query)
        self.assertIn("volume = item_daily_stats.volume + EXCLUDED.volume", cursor.query)
        self.assertEqual(cursor.params["quantity"], 7)

    async def test_record_price_bulk_writes_quantities_to_daily_volume(self):
        cursor = FakeCursor()

        with patch(
            "poe2scout.db.repositories.price_log_repository."
            "record_price.BaseRepository.get_db_cursor",
            return_value=FakeCursorContext(cursor),
        ):
            await record_price_bulk(
                [
                    RecordPriceModel(
                        item_id=10,
                        league_id=20,
                        realm_id=30,
                        price=4.5,
                        quantity=7,
                    )
                ],
                epoch=1777046400,
            )

        self.assertIn("quantity AS volume", cursor.query)
        self.assertIn("volume = item_daily_stats.volume + EXCLUDED.volume", cursor.query)
        self.assertEqual(cursor.params["quantities"], [7])


if __name__ == "__main__":
    unittest.main()
