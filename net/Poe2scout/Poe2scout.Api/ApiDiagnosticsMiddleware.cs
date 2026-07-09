using System.Diagnostics;

namespace Poe2scout.Api;

public sealed class ApiDiagnosticsMiddleware(RequestDelegate next, ApiDiagnostics diagnostics)
{
  public async Task InvokeAsync(HttpContext context)
  {
    var startedAt = Stopwatch.GetTimestamp();

    try
    {
      await next(context);
    }
    catch
    {
      diagnostics.RequestFailed(
        StatusCodes.Status500InternalServerError,
        GetElapsedMilliseconds(startedAt));
      throw;
    }

    var durationMs = GetElapsedMilliseconds(startedAt);
    if (context.Response.StatusCode >= StatusCodes.Status400BadRequest)
    {
      diagnostics.RequestFailed(context.Response.StatusCode, durationMs);
      return;
    }

    diagnostics.RequestCompleted(context.Response.StatusCode, durationMs);
  }

  private static int GetElapsedMilliseconds(long startedAt)
  {
    return (int)Math.Min(Stopwatch.GetElapsedTime(startedAt).TotalMilliseconds, int.MaxValue);
  }
}
