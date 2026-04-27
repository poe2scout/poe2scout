from datetime import datetime
from typing import Optional

from poe2scout.db.repositories.base_repository import RepositoryModel
from poe2scout.db.repositories.unique_item_repository.get_all_unique_items import UniqueItem


class PriceLogEntry(RepositoryModel):
    price: float
    time: datetime
    quantity: int


class CurrencyItem(RepositoryModel):
    currency_item_id: int
    item_id: int
    currency_category_id: int
    api_id: str
    text: str
    category_api_id: str
    icon_url: Optional[str] = None
    item_metadata: Optional[dict] = None


class CurrencyItemExtended(CurrencyItem):
    price_logs: list[PriceLogEntry | None]
    current_price: Optional[float] = None
    current_quantity: Optional[int] = None


class UniqueItemExtended(UniqueItem):
    price_logs: list[PriceLogEntry | None]
    current_price: Optional[float] = None
    current_quantity: Optional[int] = None
