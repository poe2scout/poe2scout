using System.Diagnostics;
using System.Diagnostics.Metrics;

namespace Poe2scout.Api;

public enum ApiRequestOutcome
{
  Success,
  ClientError,
  ServerError
}

public sealed class ApiDiagnostics
{
  public const string MeterName = "Poe2scout.Api";
  public const string RequestCountInstrumentName = "poe2scout.api.http.requests";
  public const string RequestDurationInstrumentName = "poe2scout.api.http.request.duration";

  private static readonly EventId RequestFailedEvent = new(1001, "ApiRequestFailed");
  private static readonly EventId RequestSlowEvent = new(1002, "ApiRequestSlow");

  private readonly Counter<long> requestCount;
  private readonly Histogram<double> requestDuration;
  private readonly ILogger<ApiDiagnostics> logger;
  private readonly int slowRequestThresholdMs;

  public ApiDiagnostics(IMeterFactory meterFactory, ILogger<ApiDiagnostics> logger, ApiConfig config)
  {
    var meter = meterFactory.Create(MeterName);
    this.logger = logger;
    slowRequestThresholdMs = config.SlowRequestThresholdMs;

    requestCount = meter.CreateCounter<long>(
      RequestCountInstrumentName,
      "{request}",
      "Completed product API requests.");
    requestDuration = meter.CreateHistogram<double>(
      RequestDurationInstrumentName,
      "s",
      "Product API request duration.");
  }

  public static ApiRequestOutcome ClassifyOutcome(int statusCode)
  {
    if (statusCode >= StatusCodes.Status500InternalServerError)
    {
      return ApiRequestOutcome.ServerError;
    }

    return statusCode >= StatusCodes.Status400BadRequest
      ? ApiRequestOutcome.ClientError
      : ApiRequestOutcome.Success;
  }

  public void RecordRequest(
    string route,
    string method,
    int statusCode,
    ApiRequestOutcome outcome,
    TimeSpan duration,
    string requestPath,
    Exception? exception = null)
  {
    var outcomeValue = GetOutcomeValue(outcome);
    var countTags = new TagList
    {
      { "http.route", route },
      { "http.request.method", method },
      { "http.response.status_code", statusCode },
      { "request.outcome", outcomeValue }
    };
    requestCount.Add(1, countTags);

    var durationTags = new TagList
    {
      { "http.route", route },
      { "http.request.method", method },
      { "request.outcome", outcomeValue }
    };
    requestDuration.Record(duration.TotalSeconds, durationTags);

    var durationMs = (int)Math.Min(Math.Round(duration.TotalMilliseconds), int.MaxValue);
    if (outcome == ApiRequestOutcome.ServerError)
    {
      logger.LogError(
        RequestFailedEvent,
        exception,
        "API request failed: {HttpRequestMethod} {HttpRoute} returned {HttpResponseStatusCode} in {DurationMs} ms for {RequestPath}. Outcome {RequestOutcome}.",
        method,
        route,
        statusCode,
        durationMs,
        requestPath,
        outcomeValue);
      return;
    }

    if (durationMs >= slowRequestThresholdMs)
    {
      logger.LogWarning(
        RequestSlowEvent,
        "Slow API request: {HttpRequestMethod} {HttpRoute} returned {HttpResponseStatusCode} in {DurationMs} ms for {RequestPath}. Outcome {RequestOutcome}.",
        method,
        route,
        statusCode,
        durationMs,
        requestPath,
        outcomeValue);
    }
  }

  private static string GetOutcomeValue(ApiRequestOutcome outcome)
  {
    return outcome switch
    {
      ApiRequestOutcome.Success => "success",
      ApiRequestOutcome.ClientError => "client_error",
      ApiRequestOutcome.ServerError => "server_error",
      _ => throw new ArgumentOutOfRangeException(nameof(outcome), outcome, null)
    };
  }
}
