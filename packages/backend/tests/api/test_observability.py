import logging
import unittest
from collections.abc import Awaitable, Callable
from unittest.mock import patch

from fastapi.testclient import TestClient
from slowapi.extension import StrOrCallableStr

from poe2scout.api.application import ApiDependencyChecks, create_app
from poe2scout.api.config import ApiServiceConfig
from poe2scout.observability.metrics import render_metrics


class CollectingHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.store[key] = value

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        return


def async_check(result: bool) -> Callable[[], Awaitable[bool]]:
    async def _check() -> bool:
        return result

    return _check


def build_app(
    *,
    db_ready: bool = True,
    redis_ready: bool = True,
    slow_request_threshold_ms: int = 10,
    application_limits: list[StrOrCallableStr] | None = None,
) -> tuple[object, FakeRedis]:
    config = ApiServiceConfig(
        dbstring="postgresql://unused",
        redis_url="redis://unused",
        secret_key="test-secret",
        slow_request_threshold_ms=slow_request_threshold_ms,
    )
    dependency_checks = ApiDependencyChecks(
        db=async_check(db_ready),
        redis=async_check(redis_ready),
    )
    fake_redis = FakeRedis()
    app = create_app(
        config,
        dependency_checks=dependency_checks,
        application_limits=application_limits,
        enable_test_routes=True,
        initialize_database_pool=False,
        start_metrics_server=False,
    )
    return app, fake_redis


def render_app_metrics(app: object) -> str:
    payload, _content_type = render_metrics(app.state.metrics_registry)
    return payload.decode("utf-8")


def metric_value(metrics_text: str, metric_name: str, *label_parts: str) -> float:
    for line in metrics_text.splitlines():
        if not line.startswith(metric_name):
            continue
        if label_parts and not all(label in line for label in label_parts):
            continue
        return float(line.rsplit(" ", 1)[1])
    raise AssertionError(f"Metric {metric_name} with labels {label_parts} not found")


class ApiObservabilityTests(unittest.TestCase):
    def test_health_live_is_always_200(self) -> None:
        app, fake_redis = build_app()
        with patch("poe2scout.api.dependancies.get_redis_client", return_value=fake_redis):
            with TestClient(app) as client:
                response = client.get("/health/live")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "api"})

    def test_health_ready_reflects_dependency_status(self) -> None:
        healthy_app, healthy_redis = build_app(db_ready=True, redis_ready=True)
        with patch("poe2scout.api.dependancies.get_redis_client", return_value=healthy_redis):
            with TestClient(healthy_app) as client:
                healthy_response = client.get("/health/ready")

        self.assertEqual(healthy_response.status_code, 200)
        self.assertEqual(
            healthy_response.json(),
            {
                "status": "ok",
                "service": "api",
                "checks": {"db": "ok", "redis": "ok"},
            },
        )

        unhealthy_app, unhealthy_redis = build_app(db_ready=False, redis_ready=True)
        with patch("poe2scout.api.dependancies.get_redis_client", return_value=unhealthy_redis):
            with TestClient(unhealthy_app) as client:
                unhealthy_response = client.get("/health/ready")

        self.assertEqual(unhealthy_response.status_code, 503)
        self.assertEqual(unhealthy_response.json()["status"], "degraded")
        self.assertEqual(unhealthy_response.json()["checks"]["db"], "error")

    def test_request_metrics_cover_status_classes_and_cache(self) -> None:
        app, fake_redis = build_app()
        with patch("poe2scout.api.dependancies.get_redis_client", return_value=fake_redis):
            with TestClient(app, raise_server_exceptions=False) as client:
                client.get("/_test/ok")
                client.get("/_test/bad-request")
                client.get("/_test/error")
                client.get("/_test/cached")
                client.get("/_test/cached")

        metrics_text = render_app_metrics(app)
        self.assertEqual(
            metric_value(
                metrics_text,
                "poe2scout_http_requests_total",
                'route_template="/_test/ok"',
                'status_code="200"',
            ),
            1.0,
        )
        self.assertEqual(
            metric_value(
                metrics_text,
                "poe2scout_http_requests_total",
                'route_template="/_test/bad-request"',
                'status_code="400"',
            ),
            1.0,
        )
        self.assertEqual(
            metric_value(
                metrics_text,
                "poe2scout_http_requests_total",
                'route_template="/_test/error"',
                'status_code="500"',
            ),
            1.0,
        )
        self.assertEqual(
            metric_value(
                metrics_text,
                "poe2scout_http_4xx_total",
                'route_template="/_test/bad-request"',
            ),
            1.0,
        )
        self.assertEqual(
            metric_value(
                metrics_text,
                "poe2scout_http_5xx_total",
                'route_template="/_test/error"',
            ),
            1.0,
        )
        self.assertEqual(
            metric_value(metrics_text, "poe2scout_redis_cache_total", 'result="miss"'),
            1.0,
        )
        self.assertEqual(
            metric_value(metrics_text, "poe2scout_redis_cache_total", 'result="hit"'),
            1.0,
        )

    def test_rate_limit_and_slow_request_counters_increment(self) -> None:
        app, fake_redis = build_app(application_limits=["1/minute"], slow_request_threshold_ms=10)
        with patch("poe2scout.api.dependancies.get_redis_client", return_value=fake_redis):
            with TestClient(app) as client:
                client.get("/_test/slow")
                second_ok = client.get("/_test/ok")
                third_rate_limited = client.get("/_test/ok")

        self.assertEqual(second_ok.status_code, 429)
        self.assertEqual(third_rate_limited.status_code, 429)
        metrics_text = render_app_metrics(app)
        self.assertEqual(
            metric_value(
                metrics_text,
                "poe2scout_http_slow_requests_total",
                'route_template="/_test/slow"',
            ),
            1.0,
        )
        self.assertEqual(
            metric_value(
                metrics_text,
                "poe2scout_http_429_total",
                'route_template="/_test/ok"',
            ),
            2.0,
        )

    def test_metrics_are_not_exposed_on_public_api_listener(self) -> None:
        app, fake_redis = build_app()
        with patch("poe2scout.api.dependancies.get_redis_client", return_value=fake_redis):
            with TestClient(app) as client:
                response = client.get("/metrics")

        self.assertEqual(response.status_code, 404)

    def test_request_logs_are_structured_without_raw_headers(self) -> None:
        app, fake_redis = build_app()
        handler = CollectingHandler()
        logger = logging.getLogger("poe2scout.api.application")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        try:
            with patch("poe2scout.api.dependancies.get_redis_client", return_value=fake_redis):
                with TestClient(app) as client:
                    response = client.get("/_test/ok", headers={"X-Request-ID": "req-123"})
        finally:
            logger.removeHandler(handler)

        self.assertEqual(response.status_code, 200)
        completion_logs = [
            record for record in handler.records if record.getMessage() == "request completed"
        ]
        self.assertTrue(completion_logs)
        completion_log = completion_logs[-1]
        self.assertEqual(completion_log.request_id, "req-123")
        self.assertEqual(completion_log.route_template, "/_test/ok")
        self.assertEqual(completion_log.status_code, 200)
        self.assertIsInstance(completion_log.duration_ms, float)
        self.assertFalse(hasattr(completion_log, "headers"))


if __name__ == "__main__":
    unittest.main()
