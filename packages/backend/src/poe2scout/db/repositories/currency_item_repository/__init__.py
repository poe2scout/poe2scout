from poe2scout.db.repositories.models import CurrencyItem
from .create_currency_category import create_currency_category
from .create_currency_item import create_currency_item
from .get_all_currency_categories import get_all_currency_categories
from .get_all_currency_items import get_all_currency_items
from .get_currency_item import get_currency_item
from .get_currency_items import get_currency_items
from .get_currency_items_by_category import get_currency_items_by_category
from .is_item_a_currency import is_item_a_currency
from .set_currency_item_metadata import set_currency_item_metadata
from .update_currency_icon_url import update_currency_icon_url


class CurrencyItemRepository:
    def __init__(self):
        self.create_currency_category = create_currency_category
        self.get_all_currency_categories = get_all_currency_categories
        self.create_currency_item = create_currency_item
        self.get_all_currency_items = get_all_currency_items
        self.get_currency_item = get_currency_item
        self.is_item_a_currency = is_item_a_currency
        self.get_currency_items_by_category = get_currency_items_by_category
        self.set_currency_item_metadata = set_currency_item_metadata
        self.update_currency_icon_url = update_currency_icon_url
        self.get_currency_items = get_currency_items

    async def get_divine_item(self) -> CurrencyItem:
        divine_item = await self.get_currency_item("divine")

        if divine_item is None:
            raise Exception("Missing divine item")

        return divine_item

    async def get_chaos_item(self) -> CurrencyItem:
        chaos_item = await self.get_currency_item("chaos")

        if chaos_item is None:
            raise Exception("Missing chaos item")

        return chaos_item

    async def get_exalted_item(self) -> CurrencyItem:
        exalted_item = await self.get_currency_item("exalted")

        if exalted_item is None:
            raise Exception("Missing exalted item")

        return exalted_item
