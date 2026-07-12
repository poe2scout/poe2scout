namespace Poe2scout.Api;

public class ApiConfig : BaseConfig
{
  public string DbConnectionString { get; private set; } = string.Empty;
  public string GrafanaEndpoint { get; private set; } = string.Empty;
  public string GrafanaApiToken { get; private set; } = string.Empty;
  public string GrafanaInstanceId { get; private set; } = string.Empty;
  public string DeploymentEnvironment { get; private set; } = string.Empty;
  public int SlowRequestThresholdMs { get; private set; } = 750;
}
