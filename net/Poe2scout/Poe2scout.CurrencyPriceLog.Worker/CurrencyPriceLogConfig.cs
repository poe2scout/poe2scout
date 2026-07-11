namespace Poe2scout.CurrencyPriceLog.Worker;

public sealed class CurrencyPriceLogConfig : BaseConfig
{
  public string DbConnectionString { get; private set; } = string.Empty;
  public string PoeApiClientId { get; private set; } = string.Empty;
  public string PoeApiClientSecret { get; private set; } = string.Empty;
  public int BackoffInitialSeconds { get; private set; } = 30;
  public int BackoffMaxSeconds { get; private set; } = 900;
}
