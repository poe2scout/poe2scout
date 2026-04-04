from typing import List
from pydantic import BaseModel

from poe2scout.db.repositories.item_repository.get_leagues import League


class TradingPair(BaseModel):
    league: str
    market_id: str
    volume_traded: dict[str, int]
    highest_stock: dict[str, int]


class CurrencyExchangeResponse(BaseModel):
    next_change_id: int
    markets: List[TradingPair]


class LeagueCurrencyPairData(BaseModel):
    league: League
    base_item: str
    target_item: str
    value_of_target_item_in_base_items: float
    quantity_of_target_item: int
