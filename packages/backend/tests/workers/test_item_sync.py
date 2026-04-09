import unittest
from unittest.mock import AsyncMock, patch

from poe2scout.db.repositories.game_repository.get_games import Game
from poe2scout.db.repositories.item_repository.get_all_base_items import BaseItem
from poe2scout.db.repositories.item_repository.get_all_item_categories import (
    ItemCategory as RepoItemCategory,
)
from poe2scout.db.repositories.item_repository.get_all_item_types import ItemType
from poe2scout.db.repositories.unique_item_repository.get_all_unique_items import UniqueItem
from poe2scout.workers.item_sync.functions.sync_items import sync_items
from poe2scout.workers.item_sync.models import Item, ItemCategory


def make_game() -> Game:
    return Game(
        game_id=2,
        api_id="poe2",
        label="Path of Exile 2",
        ggg_api_trade_identifier="poe2",
        default_league_id=7,
    )


def make_unique_item(*, is_current: bool) -> UniqueItem:
    return UniqueItem(
        unique_item_id=10,
        item_id=20,
        icon_url=None,
        text="Some text",
        name="Existing Unique",
        category_api_id="body_armour",
        item_metadata=None,
        type="Existing Type",
        is_current=is_current,
    )


def make_feed() -> list[ItemCategory]:
    return [
        ItemCategory(
            id="body_armour",
            label="Body Armour",
            entries=[
                Item(
                    type="Existing Type",
                    name="Existing Unique",
                    text="Some text",
                )
            ],
        )
    ]


class ItemSyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_existing_inactive_unique_is_reactivated_when_seen_again(self):
        item_types = [ItemType(item_type_id=1, value="Existing Type", item_category_id=1)]
        base_items = [BaseItem(base_item_id=1, item_type_id=1, game_id=2)]
        categories = [
            RepoItemCategory(item_category_id=1, api_id="body_armour", label="Body Armour")
        ]

        with (
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.item_repository.get_all_item_types",
                AsyncMock(return_value=item_types),
            ),
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.item_repository.get_all_base_items",
                AsyncMock(return_value=base_items),
            ),
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.item_repository.get_all_item_categories",
                AsyncMock(return_value=categories),
            ),
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.unique_item_repository.get_all_unique_items",
                AsyncMock(return_value=[make_unique_item(is_current=False)]),
            ),
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.unique_item_repository.set_unique_item_current",
                AsyncMock(),
            ) as set_unique_item_current,
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.item_repository.create_item",
                AsyncMock(),
            ) as create_item,
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.unique_item_repository.create_unique_item",
                AsyncMock(),
            ) as create_unique_item,
        ):
            await sync_items(make_feed(), make_game())

        set_unique_item_current.assert_awaited_once_with(10, True)
        create_item.assert_not_awaited()
        create_unique_item.assert_not_awaited()

    async def test_existing_active_unique_is_not_duplicated(self):
        item_types = [ItemType(item_type_id=1, value="Existing Type", item_category_id=1)]
        base_items = [BaseItem(base_item_id=1, item_type_id=1, game_id=2)]
        categories = [
            RepoItemCategory(item_category_id=1, api_id="body_armour", label="Body Armour")
        ]

        with (
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.item_repository.get_all_item_types",
                AsyncMock(return_value=item_types),
            ),
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.item_repository.get_all_base_items",
                AsyncMock(return_value=base_items),
            ),
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.item_repository.get_all_item_categories",
                AsyncMock(return_value=categories),
            ),
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.unique_item_repository.get_all_unique_items",
                AsyncMock(return_value=[make_unique_item(is_current=True)]),
            ),
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.unique_item_repository.set_unique_item_current",
                AsyncMock(),
            ) as set_unique_item_current,
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.item_repository.create_item",
                AsyncMock(),
            ) as create_item,
            patch(
                "poe2scout.workers.item_sync.functions.sync_items.unique_item_repository.create_unique_item",
                AsyncMock(),
            ) as create_unique_item,
        ):
            await sync_items(make_feed(), make_game())

        set_unique_item_current.assert_not_awaited()
        create_item.assert_not_awaited()
        create_unique_item.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
