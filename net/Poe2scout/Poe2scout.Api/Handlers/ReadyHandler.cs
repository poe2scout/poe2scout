using System.Data.Common;

namespace Poe2scout.Api.Handlers;

public static class ReadyHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/health/ready", CheckReadiness)
      .DisableRateLimiting();
  }

  private static async Task<IResult> CheckReadiness(DbDataSource dbDataSource, CancellationToken cancellationToken)
  {
    using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
    timeout.CancelAfter(TimeSpan.FromSeconds(2));

    try
    {
      await using var connection = await dbDataSource.OpenConnectionAsync(timeout.Token);
      await using var command = connection.CreateCommand();
      command.CommandText = "SELECT 1";
      await command.ExecuteScalarAsync(timeout.Token);

      return Results.Ok(new { status = "ok", service = "api", database = "ok" });
    }
    catch (Exception)
    {
      return Results.Json(
        new { status = "degraded", service = "api", database = "error" },
        statusCode: StatusCodes.Status503ServiceUnavailable
      );
    }
  }
}
