namespace Poe2scout.Api.Handlers;

public static class LiveHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/health/live", () => Results.Ok(new { status = "ok", service = "api" }))
      .DisableRateLimiting();
  }
}
