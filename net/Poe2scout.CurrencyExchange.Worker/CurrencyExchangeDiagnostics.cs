using System.Diagnostics;
using System.Diagnostics.Metrics;

namespace Poe2scout.CurrencyExchange.Worker;

public sealed partial class CurrencyExchangeDiagnostics
{
  public const string MeterName = "Poe2scout.CurrencyExchange";
  
  private readonly ILogger<CurrencyExchangeDiagnostics> logger;

  public CurrencyExchangeDiagnostics(IMeterFactory meterFactory, ILogger<CurrencyExchangeDiagnostics> logger, CurrencyExchangeConfig config)
  {
    var meter = meterFactory.Create(MeterName);
    this.logger = logger;
    
  }
  
  public void RecordException(Exception ex)
  {
    logger.LogError(ex, "Unexpected exception encountered.");
  }

  public void RecordUnknownBaseIds(int epoch, int realmId, IReadOnlyCollection<string> baseIds)
  {
    logger.LogWarning(
      "{epoch} | Skipping {count} unknown CDN base item IDs for realm:{realmId}: {baseIds}",
      epoch,
      baseIds.Count,
      realmId,
      string.Join(", ", baseIds.Order(StringComparer.Ordinal)));
  }
}
