namespace Poe2scout.Api;

using Poe2scout.Api.Handlers.Currencies;

public static class Routes
{
  public static void MapHandlers(this IEndpointRouteBuilder builder)
  {
    builder.MapGet();
  }
}
