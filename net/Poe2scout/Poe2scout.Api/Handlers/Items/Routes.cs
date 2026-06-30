namespace Poe2scout.Api.Handlers.Items;

public static class Routes
{
  public static void MapItemsHandlers(this IEndpointRouteBuilder builder)
  {
    GetByIdHandler.MapGet(builder);
    GetCategoriesHandler.MapGet(builder);
    GetDailyStatsHistoryHandler.MapGet(builder);
    GetHandler.MapGet(builder);
    GetPriceHistoriesHandler.MapGet(builder);
    GetPriceHistoryHandler.MapGet(builder);
  }
}