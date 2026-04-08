from __future__ import annotations

import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prometheus_client import CollectorRegistry

from poe2scout.observability.metrics import render_metrics


class _MetricsHandler(BaseHTTPRequestHandler):
    registry: CollectorRegistry

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/metrics":
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return

        payload, content_type = render_metrics(self.registry)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


class MetricsServer:
    def __init__(self, *, registry: CollectorRegistry, port: int) -> None:
        self.registry = registry
        self.port = port
        self._http_server: ThreadingHTTPServer | None = None
        self._http_thread: threading.Thread | None = None

    def start(self) -> None:
        if self._http_server is not None:
            return

        handler = type(
            "ApiMetricsHandler",
            (_MetricsHandler,),
            {"registry": self.registry},
        )
        self._http_server = ThreadingHTTPServer(("0.0.0.0", self.port), handler)
        self._http_thread = threading.Thread(
            target=self._http_server.serve_forever,
            name=f"api-metrics-{self.port}",
            daemon=True,
        )
        self._http_thread.start()

    def stop(self) -> None:
        if self._http_server is not None:
            self._http_server.shutdown()
            self._http_server.server_close()
            self._http_server = None

        if self._http_thread is not None:
            self._http_thread.join(timeout=1)
            self._http_thread = None
