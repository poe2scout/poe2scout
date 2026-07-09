namespace Poe2scout.Api.Handlers.Realms;

public static class Routes
{
  public static void MapRealmsHandlers(this IEndpointRouteBuilder builder)
  {
    var mapGroup = builder.MapGroup("").WithTags("Realms");

    GetFiltersHandler.MapGet(mapGroup);
    GetHandler.MapGet(mapGroup);
    GetLandingSplashInfoHandler.MapGet(mapGroup);
  }
}