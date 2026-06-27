using Microsoft.AspNetCore.Mvc;
using Poe2scout.Api.Helpers;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.PriceLog.Models;
using Poe2scout.Repositories.Realm;
using Poe2scout.ValidationAttributes;

namespace Poe2scout.Api.Handlers.Items;

public class GetPriceHistoryHandler
{
  public static async Task<IResult> GetPriceHistory(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] ICurrencyItemRepository currencyItemRepository,
    [FromServices] IPriceLogRepository priceLogRepository,
    [FromRoute] string realm,
    [FromRoute] string leagueName,
    [FromRoute] int itemId,
    [FromQuery, MultipleOfFour] int logCount,
    [FromQuery] DateTime? endTime,
    [FromQuery] string? referenceCurrency)
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
    
    var logFrequency = await currencyItemRepository.IsItemACurrency(itemId) ? 1 : 6;
    
    endTime ??= DateTime.UtcNow;
    
    var history = await priceLogRepository.GetItemPriceHistory(
      itemId,
      league.LeagueId,
      validatedRealm.RealmId,
      logCount,
      logFrequency,
      endTime.Value);
    
    var referenceCurrencyApiId = referenceCurrency ?? league.BaseCurrencyApiId;

    if (referenceCurrencyApiId != league.BaseCurrencyApiId)
    {
      var referenceCurrencyItem = await currencyItemRepository.GetCurrencyItem(referenceCurrencyApiId, validatedRealm.GameId);

      if (referenceCurrencyItem is null)
      {
        return TypedResults.BadRequest("Invalid reference currency.");
      }

      var referenceCurrencyHistory = await priceLogRepository.GetItemPriceHistory(
        referenceCurrencyItem.ItemId,
        league.LeagueId,
        validatedRealm.RealmId,
        logCount,
        logFrequency,
        endTime.Value);

      history = history with
      {
        PriceHistory = PriceHelper.ConvertPriceHistoryFromBase(
          history.PriceHistory,
          referenceCurrencyHistory.PriceHistory)
      };
    }

    return TypedResults.Ok(new GetPriceHistoryResponse(history));
  }

  public record GetPriceHistoryResponse(IEnumerable<GetPriceHistoryResponse.PriceEntry> PriceHistory, bool HasMore)
  {
    public GetPriceHistoryResponse(ItemPriceHistory m) : this(
      PriceHistory: m.PriceHistory.Select(h => new PriceEntry(h)),
      HasMore: m.HasMore) {} 
    
    public record PriceEntry(double Price, DateTime Time, int Quantity)
    {
      public PriceEntry(PriceLogEntry m) : this(
        Price: m.Price,
        Time: m.Time,
        Quantity: m.Quantity) {}
    }
  }
}