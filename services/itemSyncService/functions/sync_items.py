import logging
from services.itemSyncService.models import *
from services.repositories.item_repository import ItemRepository
from services.repositories.item_repository.CreateItemCategory import (
    CreateItemCategoryModel,
)
from services.repositories.item_repository.CreateBaseItem import CreateBaseItemModel
from services.repositories.item_repository.CreateItemType import CreateItemTypeModel
from services.repositories.item_repository.CreateUniqueItem import CreateUniqueItemModel
from services.repositories.item_repository.CreateItem import CreateItemModel

logger = logging.getLogger(__name__)


async def sync_items(categories: list[itemCategory]):
    repo = ItemRepository()
    logger.info("Starting item sync process...")

    async def refresh_lists(repo: ItemRepository):
        all_types = await repo.GetAllItemTypes()
        all_base_items = await repo.GetAllBaseItems()
        all_items = await repo.GetAllItems()
        all_categories = await repo.GetAllItemCategories()
        all_unique_items = await repo.GetAllUniqueItems()
        return all_types, all_base_items, all_items, all_categories, all_unique_items

    (
        all_types,
        all_base_items,
        all_items,
        all_categories,
        all_unique_items,
    ) = await refresh_lists(repo)

    for category in categories:
        logger.info(f"Processing category: {category.label} ({category.id})")
        # Create category if needed
        category_exists = any(c.apiId == category.id for c in all_categories)
        if not category_exists:
            logger.info(f"Creating new category: {category.label}, {category.id}")
            category_model = CreateItemCategoryModel(
                id=category.id, label=category.label
            )
            category_id = await repo.CreateItemCategory(category_model)
            # Only refresh categories after creating a new one
            all_categories = await repo.GetAllItemCategories()
        else:
            category_id = next(c.id for c in all_categories if c.apiId == category.id)

        for item_entry in category.entries:
            logger.info(
                f"Processing item: {item_entry.type}, {item_entry.name}, {item_entry.text}"
            )
            # Create ItemType if needed
            type_exists = any(t.value == item_entry.type for t in all_types)
            if not type_exists:
                type_model = CreateItemTypeModel(
                    value=item_entry.type, categoryId=category_id
                )
                type_id = await repo.CreateItemType(type_model)
                # Only refresh types after creating a new one
                all_types = await repo.GetAllItemTypes()
            else:
                type_id = next(t.id for t in all_types if t.value == item_entry.type)

            # Create BaseItem if needed
            base_exists = any(b.typeId == type_id for b in all_base_items)
            if not base_exists:
                base_model = CreateBaseItemModel(
                    typeId=type_id, iconUrl=None, itemMetadata=None
                )
                base_id = await repo.CreateBaseItem(base_model)
                all_base_items = await repo.GetAllBaseItems()

                item_model = CreateItemModel(baseItemId=base_id, itemType="base")
                item_id = await repo.CreateItem(item_model)
            else:
                base_id = next(b.id for b in all_base_items if b.typeId == type_id)

            # Create Item and UniqueItem if needed
            if is_unique(item_entry):
                # Create Item
                unique_exists = any(u.name == item_entry.name for u in all_unique_items)

                if not unique_exists:
                    item_model = CreateItemModel(baseItemId=base_id, itemType="unique")
                    item_id = await repo.CreateItem(item_model)

                    unique_model = CreateUniqueItemModel(
                        itemId=item_id,
                        iconUrl=None,
                        text=item_entry.text,
                        name=item_entry.name,
                    )
                    await repo.CreateUniqueItem(unique_model)
                    all_unique_items = await repo.GetAllUniqueItems()


def is_unique(item: item):
    return item.name != None
