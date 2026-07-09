namespace Poe2scout.Api.Handlers.Currencies;

public static class Routes
{
  public static void MapCurrenciesHandlers(this IEndpointRouteBuilder builder)
  {
    var mapGroup = builder.MapGroup("").WithTags("Currencies");
    
    GetByCategoryHandler.MapGet(mapGroup);
    GetHandler.MapGet(mapGroup);
    GetPairHistoryHandler.MapGet(mapGroup);
  }
}