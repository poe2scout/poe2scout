from poe2scout.db.repositories.currency_exchange_repository.create_snapshot import (
    create_snapshot,
)
from poe2scout.db.repositories.currency_exchange_repository.get_current_snapshot import (
    get_currency_exchange,
)
from poe2scout.db.repositories.currency_exchange_repository.get_current_snapshot_history import (
    get_currency_exchange_history,
)
from poe2scout.db.repositories.currency_exchange_repository.get_current_snapshot_pairs import (
    get_current_snapshot_pairs,
)
from poe2scout.db.repositories.currency_exchange_repository.get_pair_history import (
    get_pair_history,
)
from poe2scout.db.repositories.currency_exchange_repository.update_pair_histories import (
    update_pair_histories,
)


class CurrencyExchangeRepository:
    def __init__(self):
        self.create_snapshot = create_snapshot
        self.get_currency_exchange = get_currency_exchange
        self.get_currency_exchange_history = get_currency_exchange_history
        self.get_current_snapshot_pairs = get_current_snapshot_pairs
        self.get_pair_history = get_pair_history
        self.update_pair_histories = update_pair_histories
