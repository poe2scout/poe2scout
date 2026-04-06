from poe2scout.db.repositories import currency_item_repository, item_repository
from poe2scout.db.repositories.item_repository.create_base_item import CreateBaseItemModel
from poe2scout.db.repositories.currency_item_repository.create_currency_category import (
    CreateCurrencyCategoryModel,
)
from poe2scout.db.repositories.currency_item_repository.create_currency_item import (
    CreateCurrencyItemModel,
)
from poe2scout.db.repositories.item_repository.create_item_type import CreateItemTypeModel
from poe2scout.db.repositories.item_repository.create_item import CreateItemModel

import logging

from poe2scout.workers.item_sync.models import CurrencyCategory

logger = logging.getLogger(__name__)


async def sync_currencies(categories: list[CurrencyCategory], game_id: int):
    logger.info("Starting currency sync process...")

    async def refresh_lists():
        all_categories = await currency_item_repository.get_all_currency_categories()
        all_types = await item_repository.get_all_item_types()
        all_base_items = await item_repository.get_all_base_items()
        all_items = await item_repository.get_all_items()
        all_currency_items = await currency_item_repository.get_all_currency_items()
        return all_categories, all_types, all_base_items, all_items, all_currency_items

    (
        all_categories,
        all_types,
        all_base_items,
        all_items,
        all_currency_items,
    ) = await refresh_lists()

    for category in categories:
        logger.info(f"Processing currency category: {category.label or category.id}")
        if category.label is None:
            continue
        # Create currency category
        category.id = category.id.lower()
        category_exists = any(c.api_id == category.id for c in all_categories)
        if not category_exists:
            logger.info(
                f"Creating new currency category: {category.label or category.id}"
            )
            category_model = CreateCurrencyCategoryModel(
                api_id=category.id, label=category.label
            )
            category_id = await currency_item_repository.create_currency_category(category_model)
        else:
            category_id = next(
                c.currency_category_id for c in all_categories if c.api_id == category.id
            )
        (
            all_categories,
            all_types,
            all_base_items,
            all_items,
            all_currency_items,
        ) = await refresh_lists()

        for currency in category.entries:
            # Create ItemType for currency
            type_exists = any(t.value == currency.id for t in all_types)
            if currency.text == "":
                continue
            currency_category_id = next(
                c.currency_category_id for c in all_categories if c.api_id == "currency"
            )
            if not type_exists:
                type_model = CreateItemTypeModel(
                    value=currency.id, item_category_id=currency_category_id
                )
                type_id = await item_repository.create_item_type(type_model)
            else:
                type_id = next(t.item_type_id for t in all_types if t.value == currency.id)
            (
                all_categories,
                all_types,
                all_base_items,
                all_items,
                all_currency_items,
            ) = await refresh_lists()

            # Create BaseItem for currency
            base_exists = any(b.item_type_id == type_id for b in all_base_items)
            if not base_exists:
                base_model = CreateBaseItemModel(
                    item_type_id=type_id,
                    game_id=game_id,
                    icon_url=currency.image,
                    item_metadata={"id": currency.id, "text": currency.text},
                )
                base_id = await item_repository.create_base_item(base_model)

                item_model = CreateItemModel(base_item_id=base_id, item_type="base")
                item_id = await item_repository.create_item(item_model)

            else:
                base_id = next(
                    b.base_item_id for b in all_base_items if b.item_type_id == type_id
                )

            # Create CurrencyItem
            currency_exists = any(c.api_id == currency.id for c in all_currency_items)
            logger.info(f"currency: {currency} , currency_exists: {currency_exists}")
            if not currency_exists:
                # Create Item
                item_model = CreateItemModel(base_item_id=base_id, item_type="currency")
                item_id = await item_repository.create_item(item_model)

                # Safely construct the image URL
                # If currency.image is None, image_url will be None
                # Otherwise, it constructs the full URL
                image_url = (
                    f"https://web.poecdn.com/{currency.image}"
                    if currency.image is not None
                    else None
                )

                currency_model = CreateCurrencyItemModel(
                    item_id=item_id,
                    currency_category_id=category_id,
                    api_id=currency.id,
                    text=currency.text,
                    # Use the safely constructed URL (can be None)
                    image=image_url,
                )
                await currency_item_repository.create_currency_item(currency_model)

            (
                all_categories,
                all_types,
                all_base_items,
                all_items,
                all_currency_items,
            ) = await refresh_lists()
