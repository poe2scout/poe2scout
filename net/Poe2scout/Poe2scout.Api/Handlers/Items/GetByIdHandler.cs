using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.Realm;
using Poe2scout.Repositories.UniqueItem;

namespace Poe2scout.Api.Handlers.Items;

public static class GetByIdHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/{realm}/Leagues/{leagueName}/Items/{itemId:int}", GetById);
  }
  
  private static async Task<Results<Ok<GetHandler.GetItemResponse>, BadRequest<string>, NotFound<string>>> GetById(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] IUniqueItemRepository uniqueItemRepository,
    [FromServices] ICurrencyItemRepository currencyItemRepository,
    [FromServices] IPriceLogRepository priceLogRepository,
    [FromRoute] string realm,
    [FromRoute] string leagueName,
    [FromRoute] int itemId)
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
    
    var uniqueItemTask = uniqueItemRepository.GetUniqueItemByItemId(itemId, validatedRealm.GameId);
    var currencyItemTask = currencyItemRepository.GetCurrencyItemByItemId(itemId, validatedRealm.GameId);
    
    await Task.WhenAll(uniqueItemTask, currencyItemTask);

    var uniqueItem = await uniqueItemTask;
    var currencyItem = await currencyItemTask;

    if (uniqueItem is null && currencyItem is null)
    {
      return TypedResults.NotFound("Item not found.");
    }
    
    var priceLogs = await priceLogRepository.GetItemPrices(
      itemIds: [itemId],
      leagueId: league.LeagueId,
      realmId: validatedRealm.RealmId);
    
    var currentPrice = priceLogs.Count != 0 ? priceLogs[0].Price : 0;

    if (uniqueItem is not null)
    {
      return TypedResults.Ok(new GetHandler.GetItemResponse(uniqueItem, currentPrice));
    }

    if (currencyItem is not null)
    {
      return TypedResults.Ok(new GetHandler.GetItemResponse(currencyItem, currentPrice));
    }

    throw new Exception("Invalid item id.");
  }
}