from poe2scout.shared import BaseConfig


class PriceFetchConfig(BaseConfig):
    dbstring: str
    service_name: str = "unique-price-log"
    metrics_port: int = 9103
    log_json: bool = True
    log_level: str = "INFO"
    expected_interval_seconds: int = 3600
    backoff_initial_seconds: int = 30
    backoff_max_seconds: int = 900
