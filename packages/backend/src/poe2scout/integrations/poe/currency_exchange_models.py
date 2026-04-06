from decimal import Decimal
from typing import List

from pydantic import BaseModel


class CurrencyExchangeSnapshotPairData(BaseModel):
    value_traded: Decimal
    relative_price: Decimal
    volume_traded: int
    highest_stock: int
    stock_value: Decimal


class CurrencyExchangeSnapshotPair(BaseModel):
    currency_one_item_id: int
    currency_two_item_id: int
    volume: Decimal
    currency_one_data: CurrencyExchangeSnapshotPairData
    currency_two_data: CurrencyExchangeSnapshotPairData


class CurrencyExchangeSnapshot(BaseModel):
    epoch: int
    league_id: int
    realm_id: int
    pairs: List[CurrencyExchangeSnapshotPair]
    volume: Decimal = Decimal(0)
    market_cap: Decimal = Decimal(0)
