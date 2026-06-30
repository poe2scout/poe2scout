namespace Poe2scout.Api.Handlers.Currencies;

public static class Routes
{
  public static void MapCurrenciesHandlers(this IEndpointRouteBuilder builder)
  {
    GetByCategoryHandler.MapGet(builder);
    GetHandler.MapGet(builder);
    GetPairHistoryHandler.MapGet(builder);
  }
}