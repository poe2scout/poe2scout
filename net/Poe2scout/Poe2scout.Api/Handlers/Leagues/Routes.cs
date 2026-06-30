namespace Poe2scout.Api.Handlers.Leagues;

public static class Routes
{
  public static void MapLeaguesHandlers(this IEndpointRouteBuilder builder)
  {
    GetExchangeSnapshotHandler.MapGet(builder);
    GetHandler.MapGet(builder);
    GetReferenceCurrenciesHandler.MapGet(builder);
    GetSnapshotHistoryHandler.MapGet(builder);
    GetSnapshotPairsHandler.MapGet(builder);
  }
}