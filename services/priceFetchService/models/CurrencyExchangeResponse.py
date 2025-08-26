from typing import List, Tuple
from pydantic import BaseModel

from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from services.repositories.item_repository.GetLeagues import League


class TradingPair(BaseModel):
    league: str
    market_id: str
    volume_traded: dict[str, int]
    lowest_stock: dict[str, int]

class CurrencyExchangeResponse(BaseModel):
    next_change_id: int
    markets: List[TradingPair]


class LeagueCurrencyPairData(BaseModel):
    league: League
    baseItem: str
    targetItem: str
    valueOfTargetItemInBaseItems: float
    quantityOfTargetItem: int