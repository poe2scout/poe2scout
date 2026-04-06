import logging
from poe2scout.db.repositories import item_repository, unique_item_repository
from poe2scout.db.repositories.game_repository.get_games import Game
from poe2scout.db.repositories.item_repository.create_item_category import (
    CreateItemCategoryModel,
)
from poe2scout.db.repositories.item_repository.create_base_item import CreateBaseItemModel
from poe2scout.db.repositories.item_repository.create_item_type import CreateItemTypeModel
from poe2scout.db.repositories.unique_item_repository.create_unique_item import (
    CreateUniqueItemModel
)
from poe2scout.db.repositories.item_repository.create_item import CreateItemModel
from poe2scout.workers.item_sync.models import Item, ItemCategory

logger = logging.getLogger(__name__)


async def sync_items(categories: list[ItemCategory], game: Game):
    logger.info("Starting item sync process...")

    async def refresh_lists():
        all_types = await item_repository.get_all_item_types()
        all_base_items = await item_repository.get_all_base_items(game.game_id)
        all_categories = await item_repository.get_all_item_categories()
        all_unique_items = await unique_item_repository.get_all_unique_items(game.game_id)
        return all_types, all_base_items, all_categories, all_unique_items

    (
        all_types,
        all_base_items,
        all_categories,
        all_unique_items,
    ) = await refresh_lists()

    for category in categories:
        logger.info(f"Processing category: {category.label} ({category.id})")
        # Create category if needed
        category_exists = any(c.api_id == category.id for c in all_categories)
        if not category_exists:
            logger.info(f"Creating new category: {category.label}, {category.id}")
            category_model = CreateItemCategoryModel(
                api_id=category.id, label=category.label
            )
            category_id = await item_repository.create_item_category(category_model)
            # Only refresh categories after creating a new one
            all_categories = await item_repository.get_all_item_categories()
        else:
            category_id = next(
                c.item_category_id for c in all_categories if c.api_id == category.id
            )

        for item_entry in category.entries:
            logger.info(
                f"Processing item: {item_entry.type}, {item_entry.name}, {item_entry.text}"
            )
            # Create ItemType if needed
            type_exists = any(t.value == item_entry.type for t in all_types)
            if not type_exists:
                type_model = CreateItemTypeModel(
                    value=item_entry.type, item_category_id=category_id
                )
                type_id = await item_repository.create_item_type(type_model)
                # Only refresh types after creating a new one
                all_types = await item_repository.get_all_item_types()
            else:
                type_id = next(t.item_type_id for t in all_types if t.value == item_entry.type)

            # Create BaseItem if needed
            base_exists = any(b.item_type_id == type_id for b in all_base_items)
            if not base_exists:
                base_model = CreateBaseItemModel(
                    item_type_id=type_id, 
                    game_id=game.game_id,
                    icon_url=None, 
                    item_metadata=None
                )
                base_id = await item_repository.create_base_item(base_model)
                all_base_items = await item_repository.get_all_base_items(game.game_id)

                item_model = CreateItemModel(base_item_id=base_id, item_type="base")
                item_id = await item_repository.create_item(item_model)
            else:
                base_id = next(
                    b.base_item_id for b in all_base_items if b.item_type_id == type_id
                )

            # Create Item and UniqueItem if needed
            if is_unique(item_entry):
                # Create Item
                if item_entry.text is None or item_entry.name is None:
                    raise Exception("Unique item missing name / text")

                unique_exists = any(u.name == item_entry.name for u in all_unique_items)

                if not unique_exists:
                    item_model = CreateItemModel(base_item_id=base_id, item_type="unique")
                    item_id = await item_repository.create_item(item_model)

                    unique_model = CreateUniqueItemModel(
                        item_id=item_id,
                        icon_url=None,
                        text=item_entry.text,
                        name=item_entry.name,
                    )
                    await unique_item_repository.create_unique_item(unique_model)
                    all_unique_items = await unique_item_repository.get_all_unique_items(game.game_id)


def is_unique(item: Item):
    return item.name is not None
