namespace Poe2scout.CurrencyItemMapping.Worker;

public sealed class CurrencyItemMappingConfig : BaseConfig
{
  public string DbConnectionString { get; private set; } = string.Empty;
  public bool ApplyChanges { get; private set; }
  public int ApplyCommandTimeoutSeconds { get; private set; } = 900;
  public int PollIntervalMinutes { get; private set; } = 60;
  public int RePoeRefreshHours { get; private set; } = 24;
  public string RePoeBaseUrl { get; private set; } = "https://repoe-fork.github.io";
}
