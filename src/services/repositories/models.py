from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from services.repositories.item_repository.GetAllUniqueItems import UniqueItem


class PriceLogEntry(BaseModel):
    price: float
    time: datetime
    quantity: int


class CurrencyItem(BaseModel):
    id: int
    itemId: int
    currencyCategoryId: int
    apiId: str
    text: str
    categoryApiId: str
    iconUrl: Optional[str] = None
    itemMetadata: Optional[dict] = None


class CurrencyItemExtended(CurrencyItem):
    priceLogs: list[PriceLogEntry | None]
    currentPrice: Optional[float] = None


class UniqueItemExtended(UniqueItem):
    priceLogs: list[PriceLogEntry | None]
    currentPrice: Optional[float] = None
