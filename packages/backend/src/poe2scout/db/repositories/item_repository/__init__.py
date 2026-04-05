from .create_base_item import create_base_item
from .create_item import create_item
from .create_item_category import create_item_category
from .create_item_type import create_item_type
from .get_all_base_items import get_all_base_items
from .get_all_item_categories import get_all_item_categories
from .get_all_item_types import get_all_item_types
from .get_all_items import get_all_items
from .get_search_options import get_search_options


class ItemRepository:
    def __init__(self):
        self.create_base_item = create_base_item
        self.get_all_base_items = get_all_base_items
        self.create_item_category = create_item_category
        self.get_all_item_categories = get_all_item_categories
        self.create_item_type = create_item_type
        self.get_all_item_types = get_all_item_types
        self.create_item = create_item
        self.get_all_items = get_all_items
        self.get_search_options = get_search_options
