namespace Poe2scout.Api.Handlers.Leagues;

public static class Routes
{
  public static void MapLeaguesHandlers(this IEndpointRouteBuilder builder)
  {
    var mapGroup = builder.MapGroup("").WithTags("Leagues");

    GetExchangeSnapshotHandler.MapGet(mapGroup);
    GetHandler.MapGet(mapGroup);
    GetReferenceCurrenciesHandler.MapGet(mapGroup);
    GetSnapshotHistoryHandler.MapGet(mapGroup);
    GetSnapshotPairsHandler.MapGet(mapGroup);
  }
}