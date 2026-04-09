import unittest
from unittest.mock import AsyncMock, patch

from poe2scout.db.repositories.item_repository.get_all_items import Item
from poe2scout.db.repositories.league_repository.get_leagues import League
from poe2scout.db.repositories.unique_item_repository.get_all_unique_items import UniqueItem
from poe2scout.integrations.poe.client import ClientError
from poe2scout.workers.unique_price_log.exceptions import UniqueItemDelistedError
from poe2scout.workers.unique_price_log.functions.fetch_unique import PriceFetchResult
from poe2scout.workers.unique_price_log.service import fetch_prices, process_uniques


def make_league() -> League:
    return League(
        league_id=7,
        value="Standard",
        base_currency_item_id=100,
        base_currency_api_id="exalted",
        base_currency_text="Exalted Orb",
    )


def make_unique_item(
    unique_item_id: int,
    item_id: int,
    name: str,
    *,
    is_current: bool = True,
) -> UniqueItem:
    return UniqueItem(
        unique_item_id=unique_item_id,
        item_id=item_id,
        icon_url=None,
        text=f"{name} text",
        name=name,
        category_api_id="body_armour",
        item_metadata=None,
        type="Armour",
        is_current=is_current,
    )


class UniquePriceLogServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_unknown_item_name_deactivates_unique_and_continues_batch(self):
        delisted_item = make_unique_item(1, 101, "Gone Item")
        active_item = make_unique_item(2, 102, "Still Here")

        with (
            patch(
                "poe2scout.workers.unique_price_log.service.fetch_unique",
                AsyncMock(
                    side_effect=[
                        UniqueItemDelistedError(
                            delisted_item.unique_item_id,
                            delisted_item.name,
                        ),
                        PriceFetchResult(price=5, quantity=2, currency="exalted"),
                        PriceFetchResult(price=-1, quantity=0, currency="chaos"),
                        PriceFetchResult(price=-1, quantity=0, currency="divine"),
                    ]
                ),
            ),
            patch(
                "poe2scout.workers.unique_price_log.service.unique_item_repository.set_unique_item_current",
                AsyncMock(),
            ) as set_unique_item_current,
            patch(
                "poe2scout.workers.unique_price_log.service.record_price",
                AsyncMock(),
            ) as record_price,
        ):
            await process_uniques(
                [delisted_item, active_item],
                make_league(),
                AsyncMock(),
                game_id=2,
                realm_id=4,
            )

        set_unique_item_current.assert_awaited_once_with(delisted_item.unique_item_id, False)
        record_price.assert_awaited_once_with(5, active_item.item_id, 7, 4, 2)

    async def test_generic_client_error_still_fails_iteration(self):
        unique_item = make_unique_item(1, 101, "Broken Item")

        with patch(
            "poe2scout.workers.unique_price_log.service.fetch_unique",
            AsyncMock(
                side_effect=ClientError(
                    "Client error occurred - Status Code: 400 | some other validation error"
                )
            ),
        ):
            with self.assertRaises(ClientError):
                await process_uniques(
                    [unique_item],
                    make_league(),
                    AsyncMock(),
                    game_id=2,
                    realm_id=4,
                )

    async def test_fetch_prices_uses_current_unique_query_for_pricing(self):
        active_unique = make_unique_item(1, 101, "Active Item", is_current=True)
        inactive_item_id = 102

        with (
            patch(
                "poe2scout.workers.unique_price_log.service.league_repository.get_league",
                AsyncMock(return_value=make_league()),
            ),
            patch(
                "poe2scout.workers.unique_price_log.service.unique_item_repository.get_current_unique_items",
                AsyncMock(return_value=[active_unique]),
            ) as get_current_unique_items,
            patch(
                "poe2scout.workers.unique_price_log.service.currency_item_repository.get_all_currency_items",
                AsyncMock(return_value=[]),
            ),
            patch(
                "poe2scout.workers.unique_price_log.service.service_repository.get_fetched_item_ids",
                AsyncMock(return_value=[]),
            ),
            patch(
                "poe2scout.workers.unique_price_log.service.item_repository.get_all_items",
                AsyncMock(
                    return_value=[
                        Item(item_id=active_unique.item_id, base_item_id=1, item_type="unique"),
                        Item(item_id=inactive_item_id, base_item_id=2, item_type="unique"),
                    ]
                ),
            ),
            patch(
                "poe2scout.workers.unique_price_log.service.fetch_unique",
                AsyncMock(
                    side_effect=[
                        PriceFetchResult(price=5, quantity=2, currency="exalted"),
                        PriceFetchResult(price=-1, quantity=0, currency="chaos"),
                        PriceFetchResult(price=-1, quantity=0, currency="divine"),
                    ]
                ),
            ) as fetch_unique_mock,
            patch(
                "poe2scout.workers.unique_price_log.service.record_price",
                AsyncMock(),
            ) as record_price,
            patch(
                "poe2scout.workers.unique_price_log.service.asyncio.sleep",
                AsyncMock(),
            ),
        ):
            await fetch_prices(AsyncMock())

        get_current_unique_items.assert_awaited_once_with(2)
        self.assertEqual(fetch_unique_mock.await_count, 3)
        fetch_unique_mock.assert_any_await(
            active_unique,
            unittest.mock.ANY,
            unittest.mock.ANY,
            "exalted",
        )
        record_price.assert_awaited_once_with(5, active_unique.item_id, 7, 4, 2)


if __name__ == "__main__":
    unittest.main()
