using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Repositories.CurrencyExchange;
using Poe2scout.Repositories.CurrencyExchange.Models;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Leagues;

public static class GetSnapshotHistoryHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/{realm}/Leagues/{leagueName}/SnapshotHistory", GetSnapshotHistory);
  }

  private static async Task<Results<Ok<GetSnapshotHistoryResponse>, BadRequest<string>>> GetSnapshotHistory(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] ICurrencyExchangeRepository currencyExchangeRepository,
    [FromRoute] string realm,
    [FromRoute] string leagueName,
    [FromQuery] int limit,
    [FromQuery] int? endEpoch)
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

    var snapshotHistory = await currencyExchangeRepository.GetCurrencyExchangeHistory(
      league.LeagueId,
      validatedRealm.RealmId,
      endEpoch ?? (int)new DateTimeOffset(DateTime.UtcNow).ToUnixTimeSeconds(),
      limit);

    return TypedResults.Ok(new GetSnapshotHistoryResponse(
      snapshotHistory,
      league.BaseCurrencyApiId,
      league.BaseCurrencyBaseItemTypeId,
      league.BaseCurrencyText));
  }

  public record GetSnapshotHistoryResponse(
    IEnumerable<GetSnapshotHistoryResponse.DataModel> Data,
    GetSnapshotHistoryResponse.MetaModel Meta,
    string? BaseCurrencyApiId,
    string? BaseCurrencyBaseItemTypeId,
    string BaseCurrencyText)
  {
    public GetSnapshotHistoryResponse(
      CurrencyExchangeHistory model,
      string? baseCurrencyApiId,
      string? baseCurrencyBaseItemTypeId,
      string baseCurrencyText) : this(
      model.Data.Select(data => new DataModel(data)),
      new MetaModel(model.Meta.GetValueOrDefault("has_more", false)),
      baseCurrencyApiId,
      baseCurrencyBaseItemTypeId,
      baseCurrencyText) {}

    public record DataModel(int Epoch, decimal MarketCap, decimal Volume)
    {
      public DataModel(CurrencyExchangeHistoryEntry model) : this(
        model.Epoch,
        model.MarketCap,
        model.Volume) {}
    }

    public record MetaModel(bool HasMore);
  }
}
