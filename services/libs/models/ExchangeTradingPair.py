from datetime import datetime
from typing import List
from pydantic import BaseModel

class ExchangeTradingPair(BaseModel):
    CurrencyOne: str
    CurrencyTwo: str

class CurrencyStats(BaseModel):
    VolumeTraded: int
    LowestStock: int
    HighestStock: int
    LowestRatio: int
    HighestRatio: int

class ExchangeTradingPairSnapshot(BaseModel):
    ExchangeTradingPair: ExchangeTradingPair
    Stats: dict[str, CurrencyStats]