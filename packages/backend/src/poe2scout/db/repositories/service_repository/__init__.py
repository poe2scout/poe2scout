from ..service_repository.get_currency_fetch_status import get_currency_fetch_status
from ..service_repository.get_fetched_item_ids import get_fetched_item_ids
from poe2scout.db.repositories.service_repository.get_service_cache_value import (
    get_service_cache_value,
)
from poe2scout.db.repositories.service_repository.set_service_cache_value import (
    set_service_cache_value,
)
class ServiceRepository:
    def __init__(self):
        self.get_fetched_item_ids = get_fetched_item_ids
        self.get_currency_fetch_status = get_currency_fetch_status
        self.get_service_cache_value = get_service_cache_value
        self.set_service_cache_value = set_service_cache_value

