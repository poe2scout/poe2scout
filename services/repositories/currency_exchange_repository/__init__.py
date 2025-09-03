from services.repositories.currency_exchange_repository.GetCurrencyExchange import GetCurrencyExchange
from services.repositories.currency_exchange_repository.CreateSnapshot import CreateSnapshot
from services.repositories.currency_exchange_repository.GetCurrencyExchangeHistory import GetCurrencyExchangeHistory
from services.repositories.currency_exchange_repository.GetLastFetchedEpoch import GetLastFetchedEpoch

class CurrencyExchangeRepository:
    def __init__(self):
        self.GetLastFetchedEpoch = GetLastFetchedEpoch().execute
        self.CreateSnapshot = CreateSnapshot().execute
        self.GetCurrencyExchange = GetCurrencyExchange().execute
        self.GetCurrencyExchangeHistory = GetCurrencyExchangeHistory().execute