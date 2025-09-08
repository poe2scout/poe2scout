from services.repositories.currency_exchange_repository.GetPairHistory import GetPairHistory
from services.repositories.currency_exchange_repository.GetCurrentSnapshot import GetCurrencyExchange
from services.repositories.currency_exchange_repository.CreateSnapshot import CreateSnapshot
from services.repositories.currency_exchange_repository.GetCurrentSnapshotHistory import GetCurrencyExchangeHistory
from services.repositories.currency_exchange_repository.GetCurrentSnapshotPairs import GetCurrentSnapshotPairs
from services.repositories.currency_exchange_repository.GetServiceCacheValue import GetServiceCacheValue
from services.repositories.currency_exchange_repository.SetServiceCacheValue import SetServiceCacheValue
from services.repositories.item_repository import GetAllItemHistories

class CurrencyExchangeRepository:
    def __init__(self):
        self.CreateSnapshot = CreateSnapshot().execute
        self.GetCurrencyExchange = GetCurrencyExchange().execute
        self.GetCurrencyExchangeHistory = GetCurrencyExchangeHistory().execute
        self.GetServiceCacheValue = GetServiceCacheValue().execute
        self.SetServiceCacheValue = SetServiceCacheValue().execute
        self.GetCurrentSnapshotPairs = GetCurrentSnapshotPairs().execute
        self.GetPairHistory = GetPairHistory().execute
