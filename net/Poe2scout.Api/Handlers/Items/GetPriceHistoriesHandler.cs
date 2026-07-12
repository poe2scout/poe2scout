using Microsoft.AspNetCore.Mvc;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Items;

public static class GetPriceHistoriesHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/{realm}/Leagues/{leagueName}/Items/PriceHistory", GetPriceHistories);
  }

  private static async Task<IResult> GetPriceHistories(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] IPriceLogRepository priceLogRepository,
    [FromRoute] string realm,
    [FromRoute] string leagueName)
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
    
    var itemHistories = await priceLogRepository.GetAllItemHistories(league.LeagueId, validatedRealm.RealmId);
    
    return TypedResults.Ok(new GetItemPriceHistoriesResponse(itemHistories));
  }

  public record GetItemPriceHistoriesResponse(IEnumerable<GetItemPriceHistoriesResponse.ItemHistory> ItemHistories)
  {
    public GetItemPriceHistoriesResponse(IReadOnlyList<Repositories.PriceLog.Models.ItemHistory> m) : this(
      ItemHistories: m.Select(i => new ItemHistory(i))) {}
    
    public record ItemHistory(int ItemId, IEnumerable<ItemHistory.ItemHistoryLog> History)
    {
      public ItemHistory(Repositories.PriceLog.Models.ItemHistory m) : this(
        ItemId:  m.ItemId,
        History: m.History.Select(h => new ItemHistoryLog(h))) {}
      
      public record ItemHistoryLog(decimal Price, DateTime Time, int Quantity)
      {
        public ItemHistoryLog(Repositories.PriceLog.Models.ItemHistoryLog m) : this(
          Price: m.Price,
          Time: m.Time,
          Quantity: m.Quantity) {}
      }
    }
  }
}