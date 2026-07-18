using System.Diagnostics.Metrics;

namespace Poe2scout.UniquePriceLog.Worker;

public sealed class UniquePriceLogDiagnostics
{
  public const string MeterName = "Poe2scout.UniquePriceLog";
  
  public const string SearchCountInstrumentName = "poe2scout.unique_price_log.search.count";
  public const string FetchCountInstrumentName = "poe2scout.unique_price_log.fetch.count";

  private readonly Counter<long> searchCount;
  private readonly Counter<long> fetchCount;
  
  private readonly ILogger<UniquePriceLogDiagnostics> logger;

  public UniquePriceLogDiagnostics(IMeterFactory meterFactory, ILogger<UniquePriceLogDiagnostics> logger, UniquePriceLogConfig config)
  {
    var meter = meterFactory.Create(MeterName);
    this.logger = logger;

    searchCount = meter.CreateCounter<long>(
      SearchCountInstrumentName,
      "{request}",
      "Completed trade api search requests.");
    
    fetchCount = meter.CreateCounter<long>(
      FetchCountInstrumentName,
      "{request}",
      "Completed trade api fetch requests.");
  }

  public void RecordSearch()
  {
    searchCount.Add(1);
  }
  
  public void RecordFetch()
  {
    fetchCount.Add(1);
  }

  public void RecordFailure(string itemName)
  {
    logger.LogWarning("Failed to invoke request: {ItemName}", itemName);
  }

  public void RecordException(Exception ex)
  {
    logger.LogError(ex, "Unexpected exception encountered.");
  }
}
