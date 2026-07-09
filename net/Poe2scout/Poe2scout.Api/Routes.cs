using Poe2scout.Api.Handlers;
using Poe2scout.Api.Handlers.Currencies;
using Poe2scout.Api.Handlers.Items;
using Poe2scout.Api.Handlers.Leagues;
using Poe2scout.Api.Handlers.Realms;
using Poe2scout.Api.Handlers.Uniques;

namespace Poe2scout.Api;

public static class Routes
{
  public static void MapHandlers(this IEndpointRouteBuilder builder)
  {
    builder.MapCurrenciesHandlers();
    builder.MapItemsHandlers();
    builder.MapLeaguesHandlers();
    builder.MapRealmsHandlers();
    builder.MapUniquesRoutes();

    ReadyHandler.MapGet(builder);
    LiveHandler.MapGet(builder);
  }
}
