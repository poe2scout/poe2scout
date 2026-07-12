using Microsoft.Extensions.Configuration;

namespace Poe2scout.CurrencyPriceLog.Worker.Tests;

internal static class TestConfig
{
  public static CurrencyPriceLogConfig Create(
    int initialBackoff = 30,
    int maximumBackoff = 900)
  {
    var configuration = new ConfigurationBuilder()
      .AddInMemoryCollection(new Dictionary<string, string?>
      {
        ["DbConnectionString"] = "Host=test",
        ["PoeApiClientId"] = "client-id",
        ["PoeApiClientSecret"] = "client-secret",
        ["BackoffInitialSeconds"] = initialBackoff.ToString(),
        ["BackoffMaxSeconds"] = maximumBackoff.ToString()
      })
      .Build();
    return BaseConfig.FromConfig<CurrencyPriceLogConfig>(configuration);
  }
}
