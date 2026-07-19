using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using Poe2scout;
using Poe2scout.CurrencyExchange.Worker;
using Poe2scout.CurrencyExchange.Worker.Ioc;
using Poe2scout.Repositories;

var builder = Host.CreateApplicationBuilder(args);
var config = BaseConfig.FromConfig<CurrencyExchangeConfig>(builder.Configuration);

builder.Services.AddSingleton(config);
builder.Services.AddDataSource(config.DbConnectionString);
builder.Services.AddPoe2scoutRepositories();
builder.Services
  .AddHttpClient<ICurrencyExchangeClient, PoeCurrencyExchangeClient>()
  .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
  {
    PooledConnectionLifetime = TimeSpan.FromMinutes(15)
  });

builder.Services.AddSingleton<CurrencyExchangeDiagnostics>();

builder.Services.AddOpenTelemetry()
  .ConfigureResource(resource => resource
    .AddService("poe2scout.currency_exchange", serviceNamespace: "Poe2scout.CurrencyExchange")
    .AddAttributes([
      new KeyValuePair<string, object>("deployment.environment", config.DeploymentEnvironment)]))
  .WithMetrics(metrics =>
  {
    metrics.AddMeter(CurrencyExchangeDiagnostics.MeterName);
    metrics.AddOtlpExporter(options => options.ApplyGrafanaOptions(config, "metrics"));
  });

builder.Logging.AddOpenTelemetry(logging =>
{
  logging.IncludeFormattedMessage = true;
  logging.IncludeScopes = true;
  logging.AddOtlpExporter(options => options.ApplyGrafanaOptions(config, "logs"));
});

builder.Services.AddHostedService<CurrencyExchangeWorker>();

await builder.Build().RunAsync();
