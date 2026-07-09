using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.Game;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Realms;

public static class GetLandingSplashInfoHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/Realms/{realm}/LandingSplashInfo", GetLandingSplashInfo);
  }
  
  private static readonly List<string> importantApiIds = ["mirror", "divine", "exalted", "annul"];

  private static async Task<Results<Ok<GetLandingSplashInfoResponse>, BadRequest<string>>> GetLandingSplashInfo(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ICurrencyItemRepository currencyItemRepository,
    [FromServices] IGameRepository gameRepository,
    [FromServices] IPriceLogRepository priceLogRepository,
    [FromRoute] string realm)
  {
    var validatedRealm = await realmRepository.GetRealm(realm);
    if (validatedRealm is null)
    {
      return TypedResults.BadRequest("Invalid realm.");
    }

    var items = await currencyItemRepository.GetCurrencyItems(importantApiIds, validatedRealm.GameId);
    var itemIds = items.Select(item => item.ItemId).ToList();
    var defaultLeagueId = await gameRepository.GetDefaultLeague(validatedRealm.GameId);
    var priceLogs = await priceLogRepository.GetItemPriceLogs(itemIds, defaultLeagueId, validatedRealm.RealmId);

    var responseItems = items
      .Select(item => new GetLandingSplashInfoResponse.Item(item, priceLogs[item.ItemId]))
      .OrderByDescending(item => item.CurrentPrice ?? 0)
      .ToList();

    return TypedResults.Ok(new GetLandingSplashInfoResponse(responseItems));
  }

  public record GetLandingSplashInfoResponse(List<GetLandingSplashInfoResponse.Item> Items)
  {
    public record Item(
      int CurrencyItemId,
      int ItemId,
      int CurrencyCategoryId,
      string ApiId,
      string Text,
      string CategoryApiId,
      string? IconUrl,
      Dictionary<string, object>? ItemMetadata,
      IEnumerable<Item.PriceLogEntry?> PriceLogs,
      double? CurrentPrice)
    {
      public Item(CurrencyItem item, IReadOnlyList<Models.PriceLogEntry?> priceLogs) : this(
        item.CurrencyItemId,
        item.ItemId,
        item.CurrencyCategoryId,
        item.ApiId,
        item.Text,
        item.CategoryApiId,
        item.IconUrl,
        item.ItemMetadata,
        priceLogs.Select(priceLog => priceLog is null ? null : new PriceLogEntry(priceLog)),
        priceLogs.FirstOrDefault(priceLog => priceLog is not null)?.Price) {}

      public record PriceLogEntry(double Price, DateTime Time, int Quantity)
      {
        public PriceLogEntry(Poe2scout.Models.PriceLogEntry model) : this(
          model.Price,
          model.Time,
          model.Quantity) {}
      }
    }
  }
}
