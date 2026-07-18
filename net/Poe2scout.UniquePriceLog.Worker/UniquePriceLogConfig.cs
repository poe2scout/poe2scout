namespace Poe2scout.UniquePriceLog.Worker;

public sealed class UniquePriceLogConfig : BaseConfig
{
  public string DbConnectionString { get; private set; } = string.Empty;
  public int BackoffInitialSeconds { get; private set; } = 30;
  public int BackoffMaxSeconds { get; private set; } = 900;
  public string DeploymentEnvironment { get; private set; } = string.Empty;
  public string GrafanaEndpoint { get; private set; } = string.Empty;
  public string GrafanaApiToken { get; private set; } = string.Empty;
  public string GrafanaInstanceId { get; private set; } = string.Empty;

}
