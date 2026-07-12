using System.Diagnostics;

namespace Poe2scout.Api;

public sealed class ApiDiagnosticsMiddleware(RequestDelegate next, ApiDiagnostics diagnostics)
{
  public async Task InvokeAsync(HttpContext context)
  {
    var endpoint = context.GetEndpoint();
    var route = GetInstrumentedRoute(endpoint, context.Request.Method);
    if (route is null)
    {
      await next(context);
      return;
    }

    var startedAt = Stopwatch.GetTimestamp();

    try
    {
      await next(context);
    }
    catch (Exception exception)
    {
      diagnostics.RecordRequest(
        route,
        context.Request.Method,
        StatusCodes.Status500InternalServerError,
        ApiRequestOutcome.ServerError,
        Stopwatch.GetElapsedTime(startedAt),
        context.Request.Path.Value ?? string.Empty,
        exception);
      throw;
    }

    diagnostics.RecordRequest(
      route,
      context.Request.Method,
      context.Response.StatusCode,
      ApiDiagnostics.ClassifyOutcome(context.Response.StatusCode),
      Stopwatch.GetElapsedTime(startedAt),
      context.Request.Path.Value ?? string.Empty);
  }

  private static string? GetInstrumentedRoute(Endpoint? endpoint, string method)
  {
    if (HttpMethods.IsOptions(method) ||
        endpoint is not RouteEndpoint routeEndpoint ||
        endpoint.Metadata.GetMetadata<ExcludeFromApiDiagnosticsMetadata>() is not null)
    {
      return null;
    }

    return routeEndpoint.RoutePattern.RawText;
  }
}
