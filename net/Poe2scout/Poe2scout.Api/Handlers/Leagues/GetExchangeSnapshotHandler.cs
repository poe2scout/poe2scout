using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Repositories.CurrencyExchange;
using Poe2scout.Repositories.CurrencyExchange.Models;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Leagues;

public static class GetExchangeSnapshotHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/{realm}/Leagues/{leagueName}/ExchangeSnapshot", GetExchangeSnapshot);
  }

  private static async Task<Results<Ok<GetExchangeSnapshotResponse>, BadRequest<string>, NotFound<string>>> GetExchangeSnapshot(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] ICurrencyExchangeRepository currencyExchangeRepository,
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

    var snapshot = await currencyExchangeRepository.GetCurrencyExchange(league.LeagueId, validatedRealm.RealmId);
    if (snapshot is null)
    {
      return TypedResults.NotFound("No data for given league.");
    }

    return TypedResults.Ok(new GetExchangeSnapshotResponse(
      snapshot,
      league.BaseCurrencyApiId,
      league.BaseCurrencyText));
  }

  public record GetExchangeSnapshotResponse(
    int Epoch,
    decimal Volume,
    decimal MarketCap,
    string BaseCurrencyApiId,
    string BaseCurrencyText)
  {
    public GetExchangeSnapshotResponse(CurrencyExchangeData model, string baseCurrencyApiId, string baseCurrencyText) : this(
      model.Epoch,
      model.Volume,
      model.MarketCap,
      baseCurrencyApiId,
      baseCurrencyText) {}
  }
}
