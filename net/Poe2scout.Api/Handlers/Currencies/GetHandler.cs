using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Currencies;

public static class GetHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/{realm}/Leagues/{leagueName}/Currencies/{apiId}", Get);
  }

  private static async Task<Results<Ok<GetResponse>, BadRequest<string>>> Get(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] ICurrencyItemRepository currencyItemRepository,
    [FromServices] IPriceLogRepository priceLogRepository,
    [FromRoute] string realm,
    [FromRoute] string leagueName,
    [FromRoute] string apiId)
  {
    var validatedRealm = await realmRepository.GetRealm(realm);
    if (validatedRealm is null)
    {
      return TypedResults.BadRequest("Invalid realm.");
    }
    
    var league = await leagueRepository.GetLeagueByValue(leagueName, validatedRealm.GameId);
    if (league is null)
    {
      return TypedResults.BadRequest("Invalid league.");
    }
    
    var currencyItem = await currencyItemRepository.GetCurrencyItem(
      Uri.UnescapeDataString(apiId),
      validatedRealm.GameId);

    if (currencyItem is null)
    {
      return TypedResults.BadRequest("Invalid currency.");
    }
    
    var priceLogsByItemId = await priceLogRepository.GetItemPriceLogs(
      itemIds: [currencyItem.ItemId],
      leagueId: league.LeagueId,
      realmId: validatedRealm.RealmId);
    
    return TypedResults.Ok(new GetResponse(currencyItem, priceLogsByItemId[currencyItem.ItemId]));
  }

  public record GetResponse(
    int CurrencyItemId,
    int ItemId,
    int CurrencyCategoryId,
    string? ApiId,
    string? BaseItemTypeId,
    string Text,
    string CategoryApiId,
    string? IconUrl,
    Dictionary<string, object>? ItemMetadata,
    IEnumerable<GetResponse.PriceLogEntry?> PriceLogs,
    double? CurrentPrice)
  {
    public GetResponse(CurrencyItem c, IReadOnlyList<Models.PriceLogEntry?> l) : this(
      CurrencyCategoryId: c.CurrencyCategoryId,
      ItemId: c.ItemId,
      CurrencyItemId: c.CurrencyItemId,
      ApiId: c.ApiId,
      BaseItemTypeId: c.BaseItemTypeId,
      Text: c.Text,
      CategoryApiId: c.CategoryApiId,
      IconUrl: c.IconUrl,
      ItemMetadata: c.ItemMetadata,
      PriceLogs: l.Select(pl => pl is not null ? new PriceLogEntry(pl) : null),
      CurrentPrice: l.FirstOrDefault(pl => pl is not null)?.Price) { }
    
    public record PriceLogEntry(
      double Price,
      DateTime Time,
      int Quantity)
    {
      public PriceLogEntry(Models.PriceLogEntry m) : this(
        Price: m.Price,
        Time: m.Time,
        Quantity: m.Quantity) { }
    }
  }
}