namespace Poe2scout.Api.Handlers.Uniques;

public static class Routes
{
  public static void MapUniquesRoutes(this IEndpointRouteBuilder builder)
  {
    GetByCategoryHandler.MapGet(builder);
  }
}