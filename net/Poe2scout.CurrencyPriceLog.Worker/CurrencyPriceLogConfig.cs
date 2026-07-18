namespace Poe2scout.CurrencyPriceLog.Worker;

public sealed class CurrencyPriceLogConfig : BaseConfig
{
  public string DbConnectionString { get; private set; } = string.Empty;
  public string PoeApiClientId { get; private set; } = string.Empty;
  public string PoeApiClientSecret { get; private set; } = string.Empty;
  public string GrafanaEndpoint { get; private set; } = string.Empty;
  public string GrafanaApiToken { get; private set; } = string.Empty;
  public string GrafanaInstanceId { get; private set; } = string.Empty;
  public string DeploymentEnvironment { get; private set; } = string.Empty;
}
