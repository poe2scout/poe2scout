namespace Poe2scout.Api.Handlers.Realms;

public static class Routes
{
  public static void MapRealmsHandlers(this IEndpointRouteBuilder builder)
  {
    GetFiltersHandler.MapGet(builder);
    GetHandler.MapGet(builder);
    GetLandingSplashInfoHandler.MapGet(builder);
  }
}