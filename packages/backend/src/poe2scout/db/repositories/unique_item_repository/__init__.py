from ..unique_item_repository.create_unique_item import create_unique_item
from ..unique_item_repository.get_all_unique_items import get_all_unique_items
from ..unique_item_repository.get_unique_items_by_category import get_unique_items_by_category
from ..unique_item_repository.set_unique_item_metadata import set_unique_item_metadata
from ..unique_item_repository.update_unique_icon_url import update_unique_icon_url


class UniqueItemRepository:
    def __init__(self):
        self.create_unique_item = create_unique_item
        self.get_all_unique_items = get_all_unique_items
        self.get_unique_items_by_category = get_unique_items_by_category
        self.set_unique_item_metadata = set_unique_item_metadata
        self.update_unique_icon_url = update_unique_icon_url
