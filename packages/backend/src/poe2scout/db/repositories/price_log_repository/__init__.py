from ..price_log_repository.get_all_item_histories import get_all_item_histories
from ..price_log_repository.get_item_price import get_item_price
from ..price_log_repository.get_item_price_history import get_item_price_history
from ..price_log_repository.get_item_price_logs import get_item_price_logs
from ..price_log_repository.get_item_prices import get_item_prices
from ..price_log_repository.get_item_prices_in_range import get_item_prices_in_range
from ..price_log_repository.get_prices_checked import get_prices_checked
from ..price_log_repository.record_price import record_price, record_price_bulk


class PriceLogRepository:
    def __init__(self):
        self.record_price = record_price
        self.get_item_price = get_item_price
        self.get_item_price_logs = get_item_price_logs
        self.get_item_price_history = get_item_price_history
        self.record_price_bulk = record_price_bulk
        self.get_prices_checked = get_prices_checked
        self.get_item_prices_in_range = get_item_prices_in_range
        self.get_item_prices = get_item_prices
        self.get_all_item_histories = get_all_item_histories