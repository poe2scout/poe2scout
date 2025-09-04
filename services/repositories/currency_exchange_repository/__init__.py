from services.repositories.currency_exchange_repository.GetCurrencyExchange import GetCurrencyExchange
from services.repositories.currency_exchange_repository.CreateSnapshot import CreateSnapshot
from services.repositories.currency_exchange_repository.GetCurrencyExchangeHistory import GetCurrencyExchangeHistory
from services.repositories.currency_exchange_repository.GetServiceCacheValue import GetServiceCacheValue
from services.repositories.currency_exchange_repository.SetServiceCacheValue import SetServiceCacheValue

class CurrencyExchangeRepository:
    def __init__(self):
        self.CreateSnapshot = CreateSnapshot().execute
        self.GetCurrencyExchange = GetCurrencyExchange().execute
        self.GetCurrencyExchangeHistory = GetCurrencyExchangeHistory().execute
        self.GetServiceCacheValue = GetServiceCacheValue().execute
        self.SetServiceCacheValue = SetServiceCacheValue().execute