from poe2scout.shared import BaseConfig


class CurrencyExchangeServiceConfig(BaseConfig):
    dbstring: str
    POEAPI_CLIENT_ID: str
    POEAPI_CLIENT_SECRET: str
    service_name: str = "currency-exchange"
    metrics_port: int = 9104
    log_json: bool = True
    log_level: str = "INFO"
    expected_interval_seconds: int = 3600
    backoff_initial_seconds: int = 30
    backoff_max_seconds: int = 900
