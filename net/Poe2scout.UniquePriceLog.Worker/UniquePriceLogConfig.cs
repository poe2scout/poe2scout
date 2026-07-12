namespace Poe2scout.UniquePriceLog.Worker;

public sealed class UniquePriceLogConfig : BaseConfig
{
  public string DbConnectionString { get; private set; } = string.Empty;
  public int BackoffInitialSeconds { get; private set; } = 30;
  public int BackoffMaxSeconds { get; private set; } = 900;
}
