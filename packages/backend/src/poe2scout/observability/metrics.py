from __future__ import annotations

import time

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    GCCollector,
    Gauge,
    Histogram,
    PlatformCollector,
    ProcessCollector,
    generate_latest,
)


def create_registry() -> CollectorRegistry:
    registry = CollectorRegistry(auto_describe=True)
    ProcessCollector(registry=registry)
    PlatformCollector(registry=registry)
    GCCollector(registry=registry)
    return registry


def render_metrics(registry: CollectorRegistry) -> tuple[bytes, str]:
    return generate_latest(registry), CONTENT_TYPE_LATEST


class ApiMetrics:
    def __init__(self, service_name: str, registry: CollectorRegistry) -> None:
        labels = ["service"]
        self.service_name = service_name
        self.request_counter = Counter(
            "poe2scout_http_requests_total",
            "Completed HTTP requests.",
            labelnames=labels + ["method", "route_template", "status_code"],
            registry=registry,
        )
        self.request_duration = Histogram(
            "poe2scout_http_request_duration_seconds",
            "HTTP request duration by route template.",
            labelnames=labels + ["method", "route_template"],
            registry=registry,
            buckets=(0.05, 0.1, 0.25, 0.5, 0.75, 1, 2, 5, 10),
        )
        self.in_flight = Gauge(
            "poe2scout_http_in_flight_requests",
            "In-flight HTTP requests.",
            labelnames=labels,
            registry=registry,
        )
        self.client_errors = Counter(
            "poe2scout_http_4xx_total",
            "HTTP 4xx responses.",
            labelnames=labels + ["method", "route_template"],
            registry=registry,
        )
        self.server_errors = Counter(
            "poe2scout_http_5xx_total",
            "HTTP 5xx responses.",
            labelnames=labels + ["method", "route_template"],
            registry=registry,
        )
        self.rate_limited = Counter(
            "poe2scout_http_429_total",
            "HTTP 429 responses.",
            labelnames=labels + ["method", "route_template"],
            registry=registry,
        )
        self.slow_requests = Counter(
            "poe2scout_http_slow_requests_total",
            "HTTP requests above the slow request threshold.",
            labelnames=labels + ["method", "route_template"],
            registry=registry,
        )
        self.redis_cache = Counter(
            "poe2scout_redis_cache_total",
            "Redis cache lookups by result.",
            labelnames=labels + ["result"],
            registry=registry,
        )
        self.readiness_dependency = Gauge(
            "poe2scout_readiness_dependency_up",
            "Readiness dependency state.",
            labelnames=labels + ["dependency"],
            registry=registry,
        )

    def _service_labels(self) -> dict[str, str]:
        return {"service": self.service_name}

    def track_in_flight(self) -> None:
        self.in_flight.labels(**self._service_labels()).inc()

    def finish_in_flight(self) -> None:
        self.in_flight.labels(**self._service_labels()).dec()

    def observe_request(
        self,
        *,
        method: str,
        route_template: str,
        status_code: int,
        duration_seconds: float,
        slow_threshold_seconds: float,
        rate_limited: bool,
    ) -> None:
        labels = self._service_labels() | {
            "method": method,
            "route_template": route_template,
        }

        self.request_counter.labels(**labels, status_code=str(status_code)).inc()
        self.request_duration.labels(**labels).observe(duration_seconds)

        if 400 <= status_code < 500:
            self.client_errors.labels(**labels).inc()
        if status_code >= 500:
            self.server_errors.labels(**labels).inc()
        if rate_limited or status_code == 429:
            self.rate_limited.labels(**labels).inc()
        if duration_seconds >= slow_threshold_seconds:
            self.slow_requests.labels(**labels).inc()

    def record_cache(self, result: str) -> None:
        self.redis_cache.labels(**self._service_labels(), result=result).inc()

    def set_readiness(self, dependency: str, ok: bool) -> None:
        self.readiness_dependency.labels(**self._service_labels(), dependency=dependency).set(
            1 if ok else 0
        )


class WorkerMetrics:
    def __init__(self, service_name: str, registry: CollectorRegistry) -> None:
        labels = ["service"]
        self.service_name = service_name
        self.started_timestamp = Gauge(
            "poe2scout_worker_started_timestamp_seconds",
            "Unix timestamp of when the worker process started.",
            labelnames=labels,
            registry=registry,
        )
        self.last_success_timestamp = Gauge(
            "poe2scout_worker_last_success_timestamp_seconds",
            "Unix timestamp of the last successful worker iteration.",
            labelnames=labels,
            registry=registry,
        )
        self.iteration_duration = Gauge(
            "poe2scout_worker_iteration_duration_seconds",
            "Duration of the most recent worker iteration.",
            labelnames=labels,
            registry=registry,
        )
        self.iterations_total = Counter(
            "poe2scout_worker_iterations_total",
            "Worker iterations by status.",
            labelnames=labels + ["status"],
            registry=registry,
        )
        self.heartbeat_timestamp = Gauge(
            "poe2scout_worker_heartbeat_timestamp_seconds",
            "Unix timestamp of the most recent worker heartbeat.",
            labelnames=labels,
            registry=registry,
        )
        self.uncaught_exceptions = Counter(
            "poe2scout_worker_uncaught_exceptions_total",
            "Uncaught worker iteration exceptions.",
            labelnames=labels + ["exception_type"],
            registry=registry,
        )
        self.expected_interval = Gauge(
            "poe2scout_worker_expected_interval_seconds",
            "Expected successful iteration interval.",
            labelnames=labels,
            registry=registry,
        )

    def _labels(self) -> dict[str, str]:
        return {"service": self.service_name}

    def set_started(self, value: float) -> None:
        self.started_timestamp.labels(**self._labels()).set(value)

    def set_expected_interval(self, seconds: float) -> None:
        self.expected_interval.labels(**self._labels()).set(seconds)

    def set_heartbeat(self, value: float | None = None) -> None:
        self.heartbeat_timestamp.labels(**self._labels()).set(value or time.time())

    def record_success(self, duration_seconds: float) -> None:
        self.iteration_duration.labels(**self._labels()).set(duration_seconds)
        self.iterations_total.labels(**self._labels(), status="success").inc()
        self.last_success_timestamp.labels(**self._labels()).set(time.time())

    def record_failure(self, duration_seconds: float, exception_type: str) -> None:
        self.iteration_duration.labels(**self._labels()).set(duration_seconds)
        self.iterations_total.labels(**self._labels(), status="failure").inc()
        self.uncaught_exceptions.labels(**self._labels(), exception_type=exception_type).inc()
