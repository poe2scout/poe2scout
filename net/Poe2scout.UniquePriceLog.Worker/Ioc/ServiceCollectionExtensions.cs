using System.Text;
using OpenTelemetry.Exporter;

namespace Poe2scout.UniquePriceLog.Worker.Ioc;

public static class ServiceCollectionExtensions
{
  public static OtlpExporterOptions ApplyGrafanaOptions(this OtlpExporterOptions options, UniquePriceLogConfig config, string type)
  {
    var auth = Convert.ToBase64String(
      Encoding.UTF8.GetBytes($"{config.GrafanaInstanceId}:{config.GrafanaApiToken}")
    );
    options.Endpoint = new Uri($"{config.GrafanaEndpoint.TrimEnd('/')}/v1/{type}");
    options.Protocol = OtlpExportProtocol.HttpProtobuf;
    options.Headers = $"Authorization=Basic {auth}";
    
    return options;
  }
}
