from poe2scout.db.repositories.models import CurrencyItem

from .create_base_item import create_base_item
from .create_currency_category import create_currency_category
from .create_currency_item import create_currency_item
from .create_item import create_item
from .create_item_category import create_item_category
from .create_item_type import create_item_type
from .create_unique_item import create_unique_item
from .get_all_base_items import get_all_base_items
from .get_all_currency_categories import get_all_currency_categories
from .get_all_currency_items import get_all_currency_items
from .get_all_item_categories import get_all_item_categories
from .get_all_item_histories import get_all_item_histories
from .get_all_item_types import get_all_item_types
from .get_all_items import get_all_items
from .get_all_unique_base_items import get_all_unique_base_items
from .get_all_unique_items import get_all_unique_items
from .get_average_unique_price import get_average_unique_price
from .get_currency_fetch_status import get_currency_fetch_status
from .get_currency_item import get_currency_item
from .get_currency_items import get_currency_items
from .get_currency_items_by_category import get_currency_items_by_category
from .get_fetched_item_ids import get_fetched_item_ids
from .get_item_price import get_item_price
from .get_item_price_history import get_item_price_history
from .get_item_price_logs import get_item_price_logs
from .get_item_prices import get_item_prices
from .get_item_prices_in_range import get_item_prices_in_range
from .get_items_in_current_league import get_items_in_current_league
from .get_league_by_value import get_league_by_value
from .get_leagues import get_all_leagues, get_leagues
from .get_prices_checked import get_prices_checked
from .get_search_options import get_search_options
from .get_snapshot_for_league import get_snapshot_for_league
from .get_unique_items_by_base_name import get_unique_items_by_base_name
from .get_unique_items_by_category import get_unique_items_by_category
from .is_item_a_currency import is_item_a_currency
from .overwrite_category import overwrite_category
from .record_price import record_price, record_price_bulk
from .set_base_item_metadata import set_base_item_metadata
from .set_currency_item_metadata import set_currency_item_metadata
from .set_unique_item_metadata import set_unique_item_metadata
from .update_base_icon_url import update_base_item_icon_url
from .update_currency_icon_url import update_currency_icon_url
from .update_unique_icon_url import update_unique_icon_url


class ItemRepository:
    def __init__(self):
        self.create_base_item = create_base_item
        self.get_all_base_items = get_all_base_items
        self.create_currency_category = create_currency_category
        self.get_all_currency_categories = get_all_currency_categories
        self.create_currency_item = create_currency_item
        self.get_all_currency_items = get_all_currency_items
        self.create_item_category = create_item_category
        self.get_all_item_categories = get_all_item_categories
        self.create_item_type = create_item_type
        self.get_all_item_types = get_all_item_types
        self.create_unique_item = create_unique_item
        self.get_all_unique_items = get_all_unique_items
        self.create_item = create_item
        self.get_all_items = get_all_items
        self.record_price = record_price
        self.get_currency_item = get_currency_item
        self.is_item_a_currency = is_item_a_currency
        self.get_leagues = get_leagues
        self.get_item_price = get_item_price
        self.get_unique_items_by_category = get_unique_items_by_category
        self.get_currency_items_by_category = get_currency_items_by_category
        self.get_item_price_logs = get_item_price_logs
        self.get_league_by_value = get_league_by_value
        self.get_search_options = get_search_options
        self.overwrite_category = overwrite_category
        self.set_unique_item_metadata = set_unique_item_metadata
        self.update_unique_icon_url = update_unique_icon_url
        self.set_currency_item_metadata = set_currency_item_metadata
        self.update_currency_icon_url = update_currency_icon_url
        self.get_fetched_item_ids = get_fetched_item_ids
        self.get_item_price_history = get_item_price_history
        self.get_currency_items = get_currency_items
        self.set_base_item_metadata = set_base_item_metadata
        self.update_base_item_icon_url = update_base_item_icon_url
        self.get_all_unique_base_items = get_all_unique_base_items
        self.get_unique_items_by_base_name = get_unique_items_by_base_name
        self.get_average_unique_price = get_average_unique_price
        self.get_snapshot_for_league = get_snapshot_for_league
        self.record_price_bulk = record_price_bulk
        self.get_all_leagues = get_all_leagues
        self.get_prices_checked = get_prices_checked
        self.get_items_in_current_league = get_items_in_current_league
        self.get_item_prices_in_range = get_item_prices_in_range
        self.get_item_prices = get_item_prices
        self.get_currency_fetch_status = get_currency_fetch_status
        self.get_all_item_histories = get_all_item_histories

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
