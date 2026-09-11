namespace Poe2scout.Api;

public sealed class AllRequestsDiagnosticsMiddleware(RequestDelegate next, ApiDiagnostics diagnostics)
{
  public async Task InvokeAsync(HttpContext context)
  {
    var endpoint = context.GetEndpoint();
    var failed = false;
    try
    {
      await next(context);
    }
    catch
    {
      failed = true;
      throw;
    }
    finally
    {
      var route = ((context.GetEndpoint() ?? endpoint) as RouteEndpoint)?.RoutePattern.RawText;
      var statusCode = failed && !context.Response.HasStarted
        ? StatusCodes.Status500InternalServerError
        : context.Response.StatusCode;
      diagnostics.RecordAllRequest(route ?? "unmatched", context.Request.Method, statusCode);
    }
  }
}
