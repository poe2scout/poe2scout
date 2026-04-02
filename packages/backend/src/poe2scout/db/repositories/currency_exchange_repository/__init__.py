from poe2scout.db.repositories.currency_exchange_repository.GetPairHistory import (
    GetPairHistory,
)
from poe2scout.db.repositories.currency_exchange_repository.GetCurrentSnapshot import (
    GetCurrencyExchange,
)
from poe2scout.db.repositories.currency_exchange_repository.CreateSnapshot import (
    CreateSnapshot,
)
from poe2scout.db.repositories.currency_exchange_repository.GetCurrentSnapshotHistory import (
    GetCurrencyExchangeHistory,
)
from poe2scout.db.repositories.currency_exchange_repository.GetCurrentSnapshotPairs import (
    GetCurrentSnapshotPairs,
)
from poe2scout.db.repositories.currency_exchange_repository.GetServiceCacheValue import (
    GetServiceCacheValue,
)
from poe2scout.db.repositories.currency_exchange_repository.SetServiceCacheValue import (
    SetServiceCacheValue,
)
from poe2scout.db.repositories.currency_exchange_repository.UpdatePairHistories import (
    UpdatePairHistories,
)

class CurrencyExchangeRepository:
    def __init__(self):
        self.CreateSnapshot = CreateSnapshot().execute
        self.GetCurrencyExchange = GetCurrencyExchange().execute
        self.GetCurrencyExchangeHistory = GetCurrencyExchangeHistory().execute
        self.GetServiceCacheValue = GetServiceCacheValue().execute
        self.SetServiceCacheValue = SetServiceCacheValue().execute
        self.GetCurrentSnapshotPairs = GetCurrentSnapshotPairs().execute
        self.GetPairHistory = GetPairHistory().execute
        self.UpdatePairHistories = UpdatePairHistories().execute
