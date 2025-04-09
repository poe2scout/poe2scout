from services.repositories.item_repository.CreateBaseItem import CreateBaseItemModel
from services.repositories.item_repository.CreateCurrencyCategory import CreateCurrencyCategoryModel
from services.repositories.item_repository.CreateCurrencyItem import CreateCurrencyItemModel
from services.repositories.item_repository.CreateItemType import CreateItemTypeModel
from services.repositories.item_repository.CreateItem import CreateItemModel

from services.repositories.item_repository import ItemRepository
from services.itemSyncService.models import *
import logging
logger = logging.getLogger(__name__)


async def sync_currencies(categories: list[currencyCategory]):
    repo = ItemRepository()
    logger.info("Starting currency sync process...")

    async def refresh_lists(repo: ItemRepository):
        all_categories = await repo.GetAllCurrencyCategories()
        all_types = await repo.GetAllItemTypes()
        all_base_items = await repo.GetAllBaseItems()
        all_items = await repo.GetAllItems()
        all_currency_items = await repo.GetAllCurrencyItems()
        return all_categories, all_types, all_base_items, all_items, all_currency_items

    all_categories, all_types, all_base_items, all_items, all_currency_items = await refresh_lists(repo)

    for category in categories:
        logger.info(
            f"Processing currency category: {category.label or category.id}")
        if category.label == None:
            continue
        # Create currency category
        category.id = category.id.lower()
        category_exists = any(c.apiId == category.id for c in all_categories)
        if not category_exists:
            logger.info(
                f"Creating new currency category: {category.label or category.id}")
            category_model = CreateCurrencyCategoryModel(
                id=category.id, label=category.label)
            category_id = await repo.CreateCurrencyCategory(category_model)
        else:
            category_id = next(
                c.id for c in all_categories if c.apiId == category.id)
        all_categories, all_types, all_base_items, all_items, all_currency_items = await refresh_lists(repo)

        for currency in category.entries:
            # Create ItemType for currency
            type_exists = any(t.value == currency.id for t in all_types)
            if currency.text == '':
                continue
            currency_category_id = next(
                c.id for c in all_categories if c.apiId == 'currency')
            if not type_exists:
                type_model = CreateItemTypeModel(
                    value=currency.id, categoryId=currency_category_id)
                type_id = await repo.CreateItemType(type_model)
            else:
                type_id = next(
                    t.id for t in all_types if t.value == currency.id)
            all_categories, all_types, all_base_items, all_items, all_currency_items = await refresh_lists(repo)

            # Create BaseItem for currency
            base_exists = any(b.typeId == type_id for b in all_base_items)
            if not base_exists:
                base_model = CreateBaseItemModel(
                    typeId=type_id,
                    iconUrl=currency.image,
                    itemMetadata={"id": currency.id, "text": currency.text}
                )
                base_id = await repo.CreateBaseItem(base_model)
            else:
                base_id = next(
                    b.id for b in all_base_items if b.typeId == type_id)

            # Create CurrencyItem
            currency_exists = any(
                c.apiId == currency.id for c in all_currency_items)
            logger.info(f"currency: {currency} , currency_exists: {currency_exists}")
            if not currency_exists:
                # Create Item
                item_model = CreateItemModel(
                    baseItemId=base_id,
                    itemType='currency'
                )
                item_id = await repo.CreateItem(item_model)

                # Safely construct the image URL
                # If currency.image is None, image_url will be None
                # Otherwise, it constructs the full URL
                image_url = f"https://web.poecdn.com/{currency.image}" if currency.image is not None else None

                currency_model = CreateCurrencyItemModel(
                    itemId=item_id,
                    currencyCategoryId=category_id,
                    apiId=currency.id,
                    text=currency.text,
                    # Use the safely constructed URL (can be None)
                    image=image_url
                )
                await repo.CreateCurrencyItem(currency_model)

            all_categories, all_types, all_base_items, all_items, all_currency_items = await refresh_lists(repo)
