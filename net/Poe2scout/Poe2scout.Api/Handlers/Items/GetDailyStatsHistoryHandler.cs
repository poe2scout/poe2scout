using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.PriceLog.Models;
using Poe2scout.Repositories.Realm;
using Poe2scout.Repositories.UniqueItem;

namespace Poe2scout.Api.Handlers.Items;

public class GetDailyStatsHistoryHandler
{
  public static async Task<Results<Ok<GetDailyStatsHistoryResponse>, BadRequest<string>, NotFound<string>>> GetDailyStatsHistory(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] IPriceLogRepository priceLogRepository,
    [FromServices] ICurrencyItemRepository currencyItemRepository,
    [FromServices] IUniqueItemRepository uniqueItemRepository,
    [FromRoute] string realm,
    [FromRoute] string leagueName,
    [FromRoute] int itemId,
    [FromQuery, Range(1, int.MaxValue)] int dayCount,
    [FromQuery] DateTime? endDate)
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
    
    var uniqueItem = await uniqueItemRepository.GetUniqueItemByItemId(itemId, validatedRealm.GameId);
    var currencyItem = await currencyItemRepository.GetCurrencyItemByItemId(itemId, validatedRealm.GameId);

    if (uniqueItem is null && currencyItem is null)
    {
      return TypedResults.NotFound("Item does not exist");
    }
    
    var dailyStatsHistory = await priceLogRepository.GetItemDailyStatsHistory(
      itemId,
      league.LeagueId,
      validatedRealm.RealmId,
      dayCount + 1,
      endDate.HasValue ? DateOnly.FromDateTime(endDate.Value) : null);
    
    var hasMore = dailyStatsHistory.Count > dayCount;

    return TypedResults.Ok(new GetDailyStatsHistoryResponse(
      dailyStats: dailyStatsHistory.Take(dayCount),
      hasMore: hasMore,
      baseCurrencyApiId: league.BaseCurrencyApiId,
      baseCurrencyText: league.BaseCurrencyText));
  }

  public record GetDailyStatsHistoryResponse(IEnumerable<GetDailyStatsHistoryResponse.DailyStat> DailyStats, bool HasMore, string BaseCurrencyApiId, string BaseCurrencyText)
  {
    public GetDailyStatsHistoryResponse(IEnumerable<DailyStatsHistoryEntry> dailyStats, bool hasMore, string baseCurrencyApiId, string baseCurrencyText) : this(
      DailyStats: dailyStats.Select(ds => new DailyStat(ds)),
      HasMore: hasMore,
      BaseCurrencyApiId: baseCurrencyApiId,
      BaseCurrencyText: baseCurrencyText) {}
    
    public record DailyStat(
      DateOnly Time,
      double Open,
      double High,
      double Low,
      double Close,
      double Average,
      int Volume)
    {
      public DailyStat(DailyStatsHistoryEntry m) : this(
        Time: m.Day,
        Open: m.OpenPrice,
        High: m.MaxPrice,
        Low: m.MinPrice,
        Close: m.ClosePrice,
        Average: m.AvgPrice,
        Volume: m.Volume) {}
    }
  }
}
