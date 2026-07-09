# Grafana Cloud dashboards

`poe2scout-api.json` is a portable dashboard for the custom telemetry emitted by
the .NET API. It is intentionally kept outside `infra/observability`; that stack
is retired and is not the source of truth for Grafana Cloud.

## Import

1. In Grafana Cloud, open **Dashboards → New → Import**.
2. Upload `poe2scout-api.json`.
3. Select the Grafana Cloud Prometheus and Loki data sources when prompted.
4. Select a deployment environment and, optionally, one or more route templates.

The dashboard expects the API's `service.name` resource attribute to remain
`poe2scout.api` and uses `deployment.environment` for environment filtering.

## Metric contract

| Grafana Cloud metric | Meaning |
| --- | --- |
| `poe2scout_api_http_requests_total` | Completed product API requests |
| `poe2scout_api_http_request_duration_seconds_bucket` | Explicit request-duration histogram buckets |

Request counters have `http_route`, `http_request_method`,
`http_response_status_code`, and `request_outcome` labels. Duration histograms
omit the status-code label to keep their active-series count lower. Route labels
are templates, not resolved paths.

Outcomes are `success`, `client_error`, and `server_error`. Success percentage
is calculated as `success / (success + server_error)`; client errors do not
affect API reliability.

## Log contract

Normal successful requests and ordinary client errors are not logged. Search
for the messages `API request failed` and `Slow API request`; their structured
fields include route template, method, status, duration, outcome, and resolved
path without its query string. OpenTelemetry automatically adds `trace_id` and
`span_id` correlation metadata. Unhandled exceptions are attached to the
failure log record.

The slow-request threshold defaults to 750 ms. Override it with the .NET
configuration key `SlowRequestThresholdMs`.
