from decimal import Decimal
from typing import List

from pydantic import BaseModel


class CurrencyExchangeSnapshotPairData(BaseModel):
    ValueTraded: Decimal
    RelativePrice: Decimal
    VolumeTraded: int
    HighestStock: int
    StockValue: Decimal


class CurrencyExchangeSnapshotPair(BaseModel):
    CurrencyOneItemId: int
    CurrencyTwoItemId: int
    Volume: Decimal
    CurrencyOneData: CurrencyExchangeSnapshotPairData
    CurrencyTwoData: CurrencyExchangeSnapshotPairData


class CurrencyExchangeSnapshot(BaseModel):
    Epoch: int
    LeagueId: int
    Pairs: List[CurrencyExchangeSnapshotPair]
    Volume: Decimal = Decimal(0)
    MarketCap: Decimal = Decimal(0)
