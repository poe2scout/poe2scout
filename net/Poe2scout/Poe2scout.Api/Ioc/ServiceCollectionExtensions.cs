using System.Text;
using System.Threading.RateLimiting;
using OpenTelemetry.Exporter;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

namespace Poe2scout.Api.Ioc;

public static class ServiceCollectionExtensions
{
  extension(IServiceCollection services)
  {
    public void AddScoutMetrics(ApiConfig config)
    {
      services.AddOpenTelemetry()
        .ConfigureResource(resource => resource
          .AddService("poe2scout.api", serviceNamespace: "Poe2scout.Api")
          .AddAttributes([
            new KeyValuePair<string, object>("deployment.environment", config.DeploymentEnvironment)]))
        .WithTracing(tracing => tracing
          .AddAspNetCoreInstrumentation()
          .AddHttpClientInstrumentation()
          .AddOtlpExporter(options => options.ApplyGrafanaOptions(config, "traces")))
        .WithMetrics(metrics =>
        {
          metrics.AddAspNetCoreInstrumentation();
          metrics.AddRuntimeInstrumentation();
          metrics.AddHttpClientInstrumentation();
          metrics.AddOtlpExporter(options => options.ApplyGrafanaOptions(config, "metrics"));
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
              SegmentsPerWindow = 1,
              Window = TimeSpan.FromMinutes(1)
            });
        });
      });
    }
  }

  public static OtlpExporterOptions ApplyGrafanaOptions(this OtlpExporterOptions options, ApiConfig config, string type)
  {
    var auth = Convert.ToBase64String(
      Encoding.UTF8.GetBytes($"{config.GrafanaInstanceId}:{config.GrafanaApiToken}")
    );
    options.Endpoint = new Uri(new Uri(config.GrafanaEndpoint), "v1/" + type);
    options.Protocol = OtlpExportProtocol.HttpProtobuf;
    options.Headers = $"Authorization=Basic {auth}";
    
    return options;
  }
}