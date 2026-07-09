namespace Poe2scout.Api.Handlers.Uniques;

public static class Routes
{
  public static void MapUniquesRoutes(this IEndpointRouteBuilder builder)
  {
    var mapGroup = builder.MapGroup("").WithTags("Uniques");

    GetByCategoryHandler.MapGet(mapGroup);
  }
}