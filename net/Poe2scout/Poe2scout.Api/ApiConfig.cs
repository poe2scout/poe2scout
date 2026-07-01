namespace Poe2scout.Api;

public class ApiConfig : BaseConfig
{
  public string DbConnectionString { get; private set; } = string.Empty;
  public string PrometheusEndpointUrl { get; private set; } = string.Empty;
  public string ServiceName { get; private set; } = string.Empty;
}