from poe2scout.shared import BaseConfig


class ItemSyncConfig(BaseConfig):
    dbstring: str
    service_name: str = "item-sync"
    metrics_port: int = 9101
    log_json: bool = True
    log_level: str = "INFO"
    expected_interval_seconds: int = 86400
    backoff_initial_seconds: int = 30
    backoff_max_seconds: int = 900
