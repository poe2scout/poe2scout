using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using Poe2scout;
using Poe2scout.Repositories;
using Poe2scout.UniquePriceLog.Worker;
using Poe2scout.UniquePriceLog.Worker.Ioc;

var builder = Host.CreateApplicationBuilder(args);
var config = BaseConfig.FromConfig<UniquePriceLogConfig>(builder.Configuration);

builder.Services.AddSingleton(config);
builder.Services.AddDataSource(config.DbConnectionString);
builder.Services.AddPoe2scoutRepositories();
builder.Services
  .AddHttpClient<IPoeTradeClient, PoeTradeClient>()
  .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
  {
    PooledConnectionLifetime = TimeSpan.FromMinutes(15)
  });

builder.Services.AddSingleton<UniquePriceLogDiagnostics>();

builder.Services.AddOpenTelemetry()
  .ConfigureResource(resource => resource
    .AddService("poe2scout.uniquePriceLog", serviceNamespace: "Poe2scout.UniquePriceLog")
    .AddAttributes([
      new KeyValuePair<string, object>("deployment.environment", config.DeploymentEnvironment)]))
  .WithMetrics(metrics =>
  {
    metrics.AddMeter(UniquePriceLogDiagnostics.MeterName);
    metrics.AddOtlpExporter(options => options.ApplyGrafanaOptions(config, "metrics"));
  });

builder.Logging.AddOpenTelemetry(logging =>
{
  logging.IncludeFormattedMessage = true;
  logging.IncludeScopes = true;
  logging.AddOtlpExporter(options => options.ApplyGrafanaOptions(config, "logs"));
});

builder.Services.AddHostedService<UniquePriceLogWorker>();

await builder.Build().RunAsync();
