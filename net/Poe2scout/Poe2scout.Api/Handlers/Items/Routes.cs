namespace Poe2scout.Api.Handlers.Items;

public static class Routes
{
  public static void MapItemsHandlers(this IEndpointRouteBuilder builder)
  {
    var mapGroup = builder.MapGroup("").WithTags("Items");

    GetByIdHandler.MapGet(mapGroup);
    GetCategoriesHandler.MapGet(mapGroup);
    GetDailyStatsHistoryHandler.MapGet(mapGroup);
    GetHandler.MapGet(mapGroup);
    GetPriceHistoriesHandler.MapGet(mapGroup);
    GetPriceHistoryHandler.MapGet(mapGroup);
  }
}