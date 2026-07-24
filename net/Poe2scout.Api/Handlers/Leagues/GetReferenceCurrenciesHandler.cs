using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Repositories.Game;
using Poe2scout.Repositories.Game.Models;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Leagues;

public static class GetReferenceCurrenciesHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/{realm}/Leagues/{leagueName}/ReferenceCurrencies", GetReferenceCurrencies);
  }

  private static async Task<Results<Ok<List<ReferenceCurrency>>, BadRequest<string>>> GetReferenceCurrencies(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] IGameRepository gameRepository,
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

    var bridgeCurrencies = await gameRepository.GetBridgeCurrencies(validatedRealm.GameId);
    var baseCurrencies = new List<BaseCurrency>
    {
      new(
        league.BaseCurrencyItemId,
        league.BaseCurrencyApiId,
        league.BaseCurrencyBaseItemTypeId,
        league.BaseCurrencyText,
        league.BaseCurrencyIconUrl)
    };
    baseCurrencies.AddRange(bridgeCurrencies.Select(currency => new BaseCurrency(currency)));

    var bridgeItemIds = baseCurrencies
      .Where(currency => currency.ItemId != league.BaseCurrencyItemId)
      .Select(currency => currency.ItemId)
      .ToList();
    var priceRows = await priceLogRepository.GetItemPricesByLeague(
      bridgeItemIds,
      [league.LeagueId],
      validatedRealm.RealmId);
    var priceLookup = priceRows.ToDictionary(row => (row.LeagueId, row.ItemId), row => row.Price);

    return TypedResults.Ok(baseCurrencies
      .Select(currency => new ReferenceCurrency(
        currency.ApiId,
        currency.BaseItemTypeId,
        currency.Text,
        currency.IconUrl,
        currency.ItemId == league.BaseCurrencyItemId
          ? 1
          : priceLookup.GetValueOrDefault((league.LeagueId, currency.ItemId), 0)))
      .ToList());
  }

  private record BaseCurrency(
    int ItemId,
    string? ApiId,
    string? BaseItemTypeId,
    string Text,
    string? IconUrl)
  {
    public BaseCurrency(BridgeCurrency currency) : this(
      currency.ItemId,
      currency.ApiId,
      currency.BaseItemTypeId,
      currency.Text,
      currency.IconUrl) {}
  }

  public record ReferenceCurrency(
    string? ApiId,
    string? BaseItemTypeId,
    string Text,
    string? IconUrl,
    double RelativePrice);
}
