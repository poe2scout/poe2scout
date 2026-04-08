import logging
from http import HTTPStatus
import unittest

from poe2scout.observability.worker_runner import ServiceRunner
from poe2scout.observability.metrics import render_metrics


class CollectingHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def metric_value(metrics_text: str, metric_name: str, *label_parts: str) -> float:
    for line in metrics_text.splitlines():
        if not line.startswith(metric_name):
            continue
        if label_parts and not all(label in line for label in label_parts):
            continue
        return float(line.rsplit(" ", 1)[1])
    raise AssertionError(f"Metric {metric_name} with labels {label_parts} not found")


class WorkerRunnerTests(unittest.IsolatedAsyncioTestCase):
    async def test_success_and_failure_metrics_update(self) -> None:
        runner = ServiceRunner(
            service_name="test-worker",
            metrics_port=0,
            expected_interval_seconds=60,
            start_http_server=False,
        )

        async def succeed() -> None:
            return

        async def fail() -> None:
            raise RuntimeError("boom")

        await runner.execute_iteration(succeed, backoff_seconds=0)
        last_success_after_success = runner.state.last_success_timestamp
        await runner.execute_iteration(fail, backoff_seconds=0)

        payload, _content_type = render_metrics(runner.registry)
        metrics_text = payload.decode("utf-8")

        self.assertGreater(
            metric_value(
                metrics_text,
                "poe2scout_worker_started_timestamp_seconds",
                'service="test-worker"',
            ),
            0.0,
        )
        self.assertGreater(last_success_after_success, 0)
        self.assertEqual(
            metric_value(
                metrics_text,
                "poe2scout_worker_iterations_total",
                'service="test-worker"',
                'status="success"',
            ),
            1.0,
        )
        self.assertEqual(
            metric_value(
                metrics_text,
                "poe2scout_worker_iterations_total",
                'service="test-worker"',
                'status="failure"',
            ),
            1.0,
        )
        self.assertEqual(runner.state.last_success_timestamp, last_success_after_success)

    async def test_uncaught_exceptions_are_logged_and_exported(self) -> None:
        runner = ServiceRunner(
            service_name="test-worker",
            metrics_port=0,
            expected_interval_seconds=60,
            start_http_server=False,
        )
        handler = CollectingHandler()
        logger = logging.getLogger("poe2scout.observability.worker_runner")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        async def fail() -> None:
            raise ValueError("bad iteration")

        try:
            await runner.execute_iteration(fail, backoff_seconds=0)
        finally:
            logger.removeHandler(handler)

        failure_logs = [
            record for record in handler.records if record.getMessage() == "worker iteration failed"
        ]
        self.assertTrue(failure_logs)
        self.assertEqual(failure_logs[-1].exception_type, "ValueError")

        payload, _content_type = render_metrics(runner.registry)
        metrics_text = payload.decode("utf-8")
        self.assertEqual(
            metric_value(
                metrics_text,
                "poe2scout_worker_uncaught_exceptions_total",
                'service="test-worker"',
                'exception_type="ValueError"',
            ),
            1.0,
        )

    async def test_health_state_reflects_failure_without_faking_liveness(self) -> None:
        runner = ServiceRunner(
            service_name="test-worker",
            metrics_port=0,
            expected_interval_seconds=60,
            start_http_server=False,
        )
        self.assertEqual(runner.state.health_status_code(), HTTPStatus.OK)
        self.assertEqual(runner.state.as_health_payload()["status"], "ok")

        async def fail() -> None:
            raise RuntimeError("boom")

        await runner.execute_iteration(fail, backoff_seconds=0)

        self.assertEqual(runner.state.health_status_code(), HTTPStatus.SERVICE_UNAVAILABLE)
        self.assertEqual(runner.state.as_health_payload()["status"], "degraded")


if __name__ == "__main__":
    unittest.main()
