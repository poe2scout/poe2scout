from services.repositories.currency_exchange_repository.CreateSnapshot import CreateSnapshot
from services.repositories.currency_exchange_repository.GetLastFetchedEpoch import GetLastFetchedEpoch

class CurrencyExchangeRepository:
    def __init__(self):
        self.GetLastFetchedEpoch = GetLastFetchedEpoch().execute
        self.CreateSnapshot = CreateSnapshot().execute