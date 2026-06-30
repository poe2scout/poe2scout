using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.League.Models;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Leagues;

public static class GetHandler
{
  public static async Task<Results<Ok<IEnumerable<GetResponse>>, BadRequest<string>>> Get(
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ICurrencyItemRepository currencyItemRepository,
    [FromServices] IPriceLogRepository priceLogRepository,
    [FromRoute] string realm)
  {
    var validatedRealm = await realmRepository.GetRealm(realm);
    if (validatedRealm is null)
    {
      return TypedResults.BadRequest("Invalid realm.");
    }

    var leagues = await leagueRepository.GetLeagues(validatedRealm.GameId);

    var exaltedItem = await currencyItemRepository.GetExaltedItem(validatedRealm.GameId);
    var chaosItem = await currencyItemRepository.GetChaosItem(validatedRealm.GameId);
    var divineItem = await currencyItemRepository.GetDivineItem(validatedRealm.GameId);
    
    var priceRows = await priceLogRepository.GetItemPricesByLeague(
      itemIds: [chaosItem.ItemId, divineItem.ItemId],
      leagueIds: leagues.Select(l => l.LeagueId).ToList(),
      realmId: validatedRealm.RealmId);

    var itemPrices = priceRows.ToDictionary(x => (x.LeagueId, x.ItemId), x => x.Price);
    
    return TypedResults.Ok(leagues
      .Select(l =>
      {
        var divinePrice = itemPrices[(l.LeagueId, divineItem.ItemId)];
        var chaosPrice = itemPrices[(l.LeagueId, chaosItem.ItemId)];
        var chaosDivinePrice = chaosPrice != 0 ? divinePrice / chaosPrice : 50;
        
        return new GetResponse(l, exaltedItem, chaosItem, divineItem, divinePrice, chaosDivinePrice);
      }));
  }

  public record GetResponse(
    string Value,
    string ShortName,
    bool IsCurrent,
    double DivinePrice,
    double ChaosDivinePrice,
    string BaseCurrencyApiId,
    string BaseCurrencyText,
    string? BaseCurrencyIconUrl,
    string ExaltedCurrencyText,
    string? ExaltedCurrencyIconUrl,
    string DivineCurrencyText,
    string? DivineCurrencyIconUrl,
    string ChaosCurrencyText,
    string? ChaosCurrencyIconUrl,
    GetResponse.LeagueCurrency DefaultCurrency)
  {
    public record LeagueCurrency(string ApiId, string Text, string? IconUrl, double RelativePrice);

    public GetResponse(League league, CurrencyItem exalt, CurrencyItem chaos, CurrencyItem divine, double divinePrice, double chaosDivinePrice) : this(
      Value: league.Value,
      ShortName: league.ShortName,
      IsCurrent: league.CurrentLeague,
      DivinePrice: divinePrice,
      ChaosDivinePrice: chaosDivinePrice,
      BaseCurrencyApiId: league.BaseCurrencyApiId,
      BaseCurrencyText: league.BaseCurrencyText,
      BaseCurrencyIconUrl: league.BaseCurrencyIconUrl,
      ExaltedCurrencyText: exalt.Text,
      ExaltedCurrencyIconUrl: exalt.IconUrl,
      DivineCurrencyText: divine.Text,
      DivineCurrencyIconUrl: divine.IconUrl,
      ChaosCurrencyText: chaos.Text,
      ChaosCurrencyIconUrl: chaos.IconUrl,
      DefaultCurrency: new LeagueCurrency(ApiId: league.BaseCurrencyApiId, Text: league.BaseCurrencyText, IconUrl: league.BaseCurrencyIconUrl, RelativePrice: 1)) {}
  }
}