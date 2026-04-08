from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Awaitable, Callable

from prometheus_client import CollectorRegistry

from poe2scout.observability.metrics import WorkerMetrics, create_registry, render_metrics


@dataclass
class ServiceRunnerState:
    service_name: str
    started_at: float = field(default_factory=time.time)
    heartbeat_timestamp: float = 0.0
    last_success_timestamp: float = 0.0
    last_error_type: str | None = None

    def is_degraded(self) -> bool:
        return self.last_error_type is not None

    def health_status_code(self) -> HTTPStatus:
        return HTTPStatus.SERVICE_UNAVAILABLE if self.is_degraded() else HTTPStatus.OK

    def as_health_payload(self) -> dict[str, object]:
        last_success_age = (
            None
            if self.last_success_timestamp == 0.0
            else max(time.time() - self.last_success_timestamp, 0.0)
        )
        return {
            "service": self.service_name,
            "status": "degraded" if self.is_degraded() else "ok",
            "started_at": self.started_at,
            "heartbeat_timestamp": self.heartbeat_timestamp,
            "last_success_timestamp": self.last_success_timestamp,
            "last_success_age_seconds": last_success_age,
            "last_error_type": self.last_error_type,
        }


class _ProbeHandler(BaseHTTPRequestHandler):
    registry: CollectorRegistry
    state: ServiceRunnerState

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/metrics":
            payload, content_type = render_metrics(self.registry)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path in {"/health", "/health/ready"}:
            payload = json.dumps(self.state.as_health_payload()).encode("utf-8")
            self.send_response(self.state.health_status_code())
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path == "/health/live":
            payload = json.dumps({"service": self.state.service_name, "status": "ok"}).encode(
                "utf-8"
            )
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


class ServiceRunner:
    def __init__(
        self,
        *,
        service_name: str,
        metrics_port: int,
        expected_interval_seconds: float,
        registry: CollectorRegistry | None = None,
        start_http_server: bool = True,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.state = ServiceRunnerState(service_name=service_name)
        self.registry = registry or create_registry()
        self.metrics = WorkerMetrics(service_name=service_name, registry=self.registry)
        self.metrics.set_started(self.state.started_at)
        self.metrics.set_expected_interval(expected_interval_seconds)
        self.metrics.set_heartbeat()
        self._metrics_port = metrics_port
        self._start_http_server = start_http_server
        self._http_server: ThreadingHTTPServer | None = None
        self._http_thread: threading.Thread | None = None
        self._heartbeat_task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if not self._start_http_server or self._http_server is not None:
            return

        handler = type(
            "WorkerProbeHandler",
            (_ProbeHandler,),
            {"registry": self.registry, "state": self.state},
        )
        self._http_server = ThreadingHTTPServer(("0.0.0.0", self._metrics_port), handler)
        self._http_thread = threading.Thread(
            target=self._http_server.serve_forever,
            name=f"{self.state.service_name}-metrics",
            daemon=True,
        )
        self._http_thread.start()
        self.logger.info(
            "worker probe server started",
            extra={
                "event": "worker_probe_server_started",
                "service": self.state.service_name,
                "metrics_port": self._metrics_port,
            },
        )

    async def stop(self) -> None:
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

        if self._http_server is not None:
            self._http_server.shutdown()
            self._http_server.server_close()
            self._http_server = None
        if self._http_thread is not None:
            self._http_thread.join(timeout=1)
            self._http_thread = None

    async def _heartbeat_loop(self) -> None:
        while True:
            self.state.heartbeat_timestamp = time.time()
            self.metrics.set_heartbeat(self.state.heartbeat_timestamp)
            await asyncio.sleep(15)

    async def execute_iteration(
        self,
        iteration: Callable[[], Awaitable[None]],
        *,
        backoff_seconds: float = 30.0,
    ) -> bool:
        self.state.heartbeat_timestamp = time.time()
        self.metrics.set_heartbeat(self.state.heartbeat_timestamp)
        started_at = time.perf_counter()
        try:
            await iteration()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            duration_seconds = time.perf_counter() - started_at
            self.state.last_error_type = type(exc).__name__
            self.metrics.record_failure(duration_seconds, type(exc).__name__)
            self.logger.exception(
                "worker iteration failed",
                extra={
                    "event": "worker_iteration_failed",
                    "service": self.state.service_name,
                    "duration_seconds": round(duration_seconds, 6),
                    "exception_type": type(exc).__name__,
                },
            )
            await asyncio.sleep(backoff_seconds)
            return False

        duration_seconds = time.perf_counter() - started_at
        self.state.last_success_timestamp = time.time()
        self.state.last_error_type = None
        self.metrics.record_success(duration_seconds)
        self.logger.info(
            "worker iteration succeeded",
            extra={
                "event": "worker_iteration_succeeded",
                "service": self.state.service_name,
                "duration_seconds": round(duration_seconds, 6),
            },
        )
        return True

    async def run_forever(
        self,
        iteration: Callable[[], Awaitable[None]],
        *,
        backoff_initial_seconds: float = 15.0,
        backoff_max_seconds: float = 300.0,
    ) -> None:
        self.start()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.logger.info(
            "service runner started",
            extra={
                "event": "service_runner_started",
                "service": self.state.service_name,
                "metrics_port": self._metrics_port,
            },
        )
        backoff_seconds = backoff_initial_seconds
        try:
            while True:
                succeeded = await self.execute_iteration(
                    iteration,
                    backoff_seconds=backoff_seconds,
                )
                backoff_seconds = (
                    backoff_initial_seconds
                    if succeeded
                    else min(backoff_seconds * 2, backoff_max_seconds)
                )
        finally:
            self.logger.info(
                "service runner stopping",
                extra={"event": "service_runner_stopping", "service": self.state.service_name},
            )
            await self.stop()
