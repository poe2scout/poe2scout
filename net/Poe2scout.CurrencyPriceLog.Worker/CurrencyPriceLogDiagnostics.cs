using System.Diagnostics;
using System.Diagnostics.Metrics;

namespace Poe2scout.CurrencyPriceLog.Worker;

public sealed partial class CurrencyPriceLogDiagnostics
{
  public const string MeterName = "Poe2scout.CurrencyPriceLog";
  
  public const string LogCountInstrumentName = "poe2scout.currency_price_log.logs.count";
  
  private readonly Counter<long> logCount;
  
  private readonly ILogger<CurrencyPriceLogDiagnostics> logger;

  public CurrencyPriceLogDiagnostics(IMeterFactory meterFactory, ILogger<CurrencyPriceLogDiagnostics> logger, CurrencyPriceLogConfig config)
  {
    var meter = meterFactory.Create(MeterName);
    this.logger = logger;
    
    logCount = meter.CreateCounter<long>(LogCountInstrumentName);
  }

  public void RecordLogs(int epoch, int leagueId, int realmId, int count)
  {
    var logTags = new TagList
    {
      { "league_id", leagueId },
      { "realm_id", realmId },
    };
    
    logCount.Add(count, logTags);
    LogCount(epoch, count, leagueId, realmId);
  }

  public void RecordException(Exception ex)
  {
    logger.LogError(ex, "Unexpected exception encountered.");
  }
  
  public void RecordLogsAlreadyChecked(int epoch, int leagueId, int realmId)
  {
    LogLeagueAlreadyChecked(epoch, leagueId, realmId);
    LogCount(epoch, 0, leagueId, realmId);
  }

  public void RecordFetchedTooEarly(int epoch, DateTime timeUtc)
  {
    logger.LogWarning("Fetched next snapshot {epoch} early at {timeUtc}", epoch, timeUtc);
  }

  public void RecordNoMarkets(int realmId, int epoch)
  {
    logger.LogError("{epoch} No markets found for {realmId}", epoch,  realmId);
  }

  [LoggerMessage(LogLevel.Information, "{epoch} | {count} logs recorded for realm:{realmId} league:{leagueId}")]
  partial void LogCount(int epoch, int count, int leagueId, int realmId);

  [LoggerMessage(LogLevel.Warning, "{epoch} | League:{leagueId} Realm:{realmId} already checked.")]
  partial void LogLeagueAlreadyChecked(int epoch, int leagueId, int realmId);
}
