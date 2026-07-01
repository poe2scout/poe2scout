using System.Threading.RateLimiting;
using OpenTelemetry.Exporter;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;

namespace Poe2scout.Api.Ioc;

public static class ServiceCollectionExtensions
{
  extension(IServiceCollection services)
  {
    public void AddScoutMetrics(ApiConfig config)
    {
      services.AddOpenTelemetry()
        .ConfigureResource(resource => resource
          .AddService(serviceName: config.ServiceName))
        .WithMetrics(metrics =>
        {
          metrics.AddAspNetCoreInstrumentation();
          if (config.IsPrometheusEnabled)
          {
            metrics.AddOtlpExporter((exporterOptions, readerOptions) =>
            {
              exporterOptions.Endpoint = new Uri(config.PrometheusEndpointUrl);
              exporterOptions.Protocol = OtlpExportProtocol.HttpProtobuf;
              readerOptions.PeriodicExportingMetricReaderOptions.ExportIntervalMilliseconds = 1000;
            });
          }
          else
          {
            metrics.AddConsoleExporter();
          }
        });
    }

    public void AddScoutRateLimiting()
    {
      services.AddRateLimiter(options =>
      {
        options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
        {
          var userIp = context.Request.Headers["CF-Connecting-IP"].ToString();

          if (string.IsNullOrEmpty(userIp))
          {
            //TODO: Log this
            
            userIp = context.Connection.RemoteIpAddress?.ToString() ?? throw new InvalidOperationException();
          }
          
          return RateLimitPartition.GetSlidingWindowLimiter(
            partitionKey: userIp,
            factory: partition => new SlidingWindowRateLimiterOptions
            {
              AutoReplenishment = true,
              PermitLimit = 60,
              QueueLimit = 0,
              Window = TimeSpan.FromMinutes(1)
            });
        });
      });
    }
  }
}