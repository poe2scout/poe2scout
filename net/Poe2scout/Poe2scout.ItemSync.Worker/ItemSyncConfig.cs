namespace Poe2scout.ItemSync.Worker;

public sealed class ItemSyncConfig : BaseConfig
{
  public string DbConnectionString { get; private set; } = string.Empty;
  public int BackoffInitialSeconds { get; private set; } = 30;
  public int BackoffMaxSeconds { get; private set; } = 900;
}
