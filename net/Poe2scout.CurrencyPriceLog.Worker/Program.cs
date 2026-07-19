using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using Poe2scout;
using Poe2scout.CurrencyPriceLog.Worker;
using Poe2scout.CurrencyPriceLog.Worker.Ioc;
using Poe2scout.Repositories;

var builder = Host.CreateApplicationBuilder(args);
var config = BaseConfig.FromConfig<CurrencyPriceLogConfig>(builder.Configuration);

builder.Services.AddSingleton(config);
builder.Services.AddDataSource(config.DbConnectionString);
builder.Services.AddPoe2scoutRepositories();
builder.Services
  .AddHttpClient<IPoeCurrencyExchangeClient, PoeCurrencyExchangeClient>()
  .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
  {
    PooledConnectionLifetime = TimeSpan.FromMinutes(15)
  });

builder.Services.AddSingleton<CurrencyPriceLogDiagnostics>();

builder.Services.AddOpenTelemetry()
  .ConfigureResource(resource => resource
    .AddService("poe2scout.currency_price_log", serviceNamespace: "Poe2scout.CurrencyPriceLog")
    .AddAttributes([
      new KeyValuePair<string, object>("deployment.environment", builder.Environment.EnvironmentName)]))
  .WithMetrics(metrics =>
  {
    metrics.AddMeter(CurrencyPriceLogDiagnostics.MeterName);
    metrics.AddOtlpExporter(options => options.ApplyGrafanaOptions(config, "metrics"));
  });

builder.Logging.AddOpenTelemetry(logging =>
{
  logging.IncludeFormattedMessage = true;
  logging.IncludeScopes = true;
  logging.AddOtlpExporter(options => options.ApplyGrafanaOptions(config, "logs"));
});

builder.Services.AddHostedService<CurrencyPriceLogWorker>();

await builder.Build().RunAsync();
