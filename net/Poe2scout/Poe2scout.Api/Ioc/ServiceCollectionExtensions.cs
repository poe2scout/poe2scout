using System.Threading.RateLimiting;
using OpenTelemetry.Exporter;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;

namespace Poe2scout.Api.Ioc;

public static class ServiceCollectionExtensions
{
  public static void AddScoutMetrics(this IServiceCollection services, ApiConfig config)
  {
    services.AddOpenTelemetry()
      .ConfigureResource(resource => resource
        .AddService(serviceName: config.ServiceName))
      .WithMetrics(metrics => 
        metrics
          .AddAspNetCoreInstrumentation()
          .AddOtlpExporter((exporterOptions, readerOptions) =>
          {
            exporterOptions.Endpoint = new Uri(config.PrometheusEndpointUrl);
            exporterOptions.Protocol = OtlpExportProtocol.HttpProtobuf;
            readerOptions.PeriodicExportingMetricReaderOptions.ExportIntervalMilliseconds = 1000;
          }));
  }

  public static void AddScoutRateLimiting(this IServiceCollection services)
  {
    services.AddRateLimiter(options =>
    {
      options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context => 
        RateLimitPartition.GetSlidingWindowLimiter(
          partitionKey: context.Request.Headers["CF-Connecting-IP"].ToString(),
          factory: partition => new SlidingWindowRateLimiterOptions
          {
            AutoReplenishment = true,
            PermitLimit = 60,
            QueueLimit = 0,
            Window = TimeSpan.FromMinutes(1)
          }));
    });
  }
}