from poe2scout.shared import BaseConfig


class ApiServiceConfig(BaseConfig):
    dbstring: str
    redis_url: str = "redis://localhost:6379"
    local: bool = False
    metrics_port: int = 9105
    secret_key: str = "poe2scout"
    service_name: str = "api"
    log_json: bool = True
    log_level: str = "INFO"
    slow_request_threshold_ms: int = 750
    readiness_poll_interval_seconds: int = 30
