using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.Realm;
using Poe2scout.Repositories.UniqueItem;

namespace Poe2scout.Api.Handlers.Items;

public static class GetHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/{realm}/Leagues/{leagueName}/Items", Get);
  }

  private static async Task<Results<Ok<List<GetItemResponse>>, BadRequest<string>>> Get(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] IUniqueItemRepository uniqueItemRepository,
    [FromServices] ICurrencyItemRepository currencyItemRepository,
    [FromServices] IPriceLogRepository priceLogRepository,
    [FromServices] ItemsCache itemsCache,
    [FromRoute] string realm,
    [FromRoute] string leagueName)
  {
    if (itemsCache.TryGetCache(realm, leagueName, out var cache))
    {
      return TypedResults.Ok(cache);
    }
    
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
    
    var uniqueItemsTask = uniqueItemRepository.GetAllUniqueItems(validatedRealm.GameId);
    var currencyItemsTask = currencyItemRepository.GetAllCurrencyItems(validatedRealm.GameId);
    
    await Task.WhenAll(uniqueItemsTask, currencyItemsTask);
    
    var uniqueItems = await uniqueItemsTask;
    var currencyItems = await currencyItemsTask;
    
    var itemIds = new List<int>();
    itemIds.AddRange(uniqueItems.Select(x => x.ItemId));
    itemIds.AddRange(currencyItems.Select(x => x.ItemId));
    
    var priceLogsByItemId = await priceLogRepository.GetItemPrices(
      itemIds: itemIds,
      leagueId: league.LeagueId,
      realmId: validatedRealm.RealmId);
    
    var itemPrices = priceLogsByItemId.ToDictionary(x => x.ItemId, x => x.Price);

    var responses = new List<GetItemResponse>();
    responses.AddRange(uniqueItems.Select(ui => new GetItemResponse(ui, itemPrices[ui.ItemId])));
    responses.AddRange(currencyItems.Select(ci => new GetItemResponse(ci, itemPrices[ci.ItemId])));
    
    itemsCache.SetCache(leagueName, realm, responses);
    
    return TypedResults.Ok(responses);
  }
  
  public record GetItemResponse(
    int ItemId,
    string CategoryApiId,
    string Text,
    string? Name,
    string? Type,
    string? ApiId,
    string? BaseItemTypeId,
    double CurrentPrice,
    string? IconUrl)
  {
    public GetItemResponse(CurrencyItem ci, double p) : this(
      ItemId: ci.ItemId,
      CategoryApiId: ci.CategoryApiId,
      Text: ci.Text,
      Name: null,
      Type: null,
      ApiId: ci.ApiId,
      BaseItemTypeId: ci.BaseItemTypeId,
      CurrentPrice: p,
      IconUrl: ci.IconUrl) {}
    
    public GetItemResponse(UniqueItem ui, double p) : this(
      ItemId: ui.ItemId,
      CategoryApiId: ui.CategoryApiId,
      Text: ui.Text,
      Name: ui.Name,
      Type: ui.Type,
      ApiId: null,
      BaseItemTypeId: null,
      CurrentPrice: p,
      IconUrl: ui.IconUrl) {}
  }
}
