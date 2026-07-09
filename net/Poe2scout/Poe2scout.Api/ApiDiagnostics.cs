using System.Diagnostics.Metrics;

namespace Poe2scout.Api;

public class ApiDiagnostics
{
  public const string MeterName = "Poe2scout.Api";
  private readonly Histogram<int> requestDuration;
  private readonly EventCounter requestCompleted;
  private readonly EventCounter requestFailed;
  private readonly ILogger<ApiDiagnostics> logger;

  public ApiDiagnostics(IMeterFactory meterFactory, ILogger<ApiDiagnostics> logger)
  {
    var meter = meterFactory.Create(MeterName);
    this.logger = logger;
    requestDuration = meter.CreateHistogram<int>(nameof(requestDuration), "ms");
    requestCompleted = meter.CreateEventCounter(nameof(requestCompleted), 1, LogLevel.Information);
    requestFailed = meter.CreateEventCounter(nameof(requestFailed), 2, LogLevel.Warning);
  }

  public class EventCounter(Counter<int> counter, EventId eventId, LogLevel logLevel)
  {
    public EventId EventId { get; } = eventId;
    public LogLevel LogLevel { get; } = logLevel;
    
    public void Record()
    {
      counter.Add(1);
    }
  }

  public void RequestCompleted(int statusCode, int durationMs)
  {
    requestDuration.Record(durationMs);
    requestCompleted.Record();
    if (logger.IsEnabled(LogLevel.Information))
    {
      logger.Log(LogLevel.Information, requestCompleted.EventId, "Request completed with code {statusCode} and took {durationMs} ms.", statusCode, durationMs);
    }    
  }

  public void RequestFailed(int statusCode, int durationMs)
  {
    requestDuration.Record(durationMs);
    requestFailed.Record();
    if (logger.IsEnabled(requestFailed.LogLevel))
    {
      logger.Log(requestFailed.LogLevel, requestFailed.EventId, "Request failed with code {statusCode} and took {durationMs} ms.", statusCode, durationMs);
    }
  }
}

public static class MeterExtensions
{
  extension(Meter meter)
  {
    public ApiDiagnostics.EventCounter CreateEventCounter(string name, int id, LogLevel logLevel)
    {
      var counter = meter.CreateCounter<int>(ApiDiagnostics.MeterName + "." + name);
      var eventId = new EventId(id, name);

      return new ApiDiagnostics.EventCounter(counter, eventId, logLevel);
    }
  }
}