using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyExchange;
using Poe2scout.Repositories.CurrencyExchange.Models;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Leagues;

public static class GetSnapshotPairsHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/{realm}/Leagues/{leagueName}/SnapshotPairs", GetSnapshotPairs);
  }

  private static async Task<Results<Ok<List<GetSnapshotPairsResponse>>, BadRequest<string>>> GetSnapshotPairs(
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

    var snapshotPairs = await currencyExchangeRepository.GetCurrentSnapshotPairs(league.LeagueId, validatedRealm.RealmId);

    return TypedResults.Ok(snapshotPairs
      .Select(pair => new GetSnapshotPairsResponse(
        pair,
        league.BaseCurrencyApiId,
        league.BaseCurrencyBaseItemTypeId,
        league.BaseCurrencyText))
      .ToList());
  }

  public record GetSnapshotPairsResponse(
    int CurrencyExchangeSnapshotPairId,
    int CurrencyExchangeSnapshotId,
    decimal Volume,
    string? BaseCurrencyApiId,
    string? BaseCurrencyBaseItemTypeId,
    string BaseCurrencyText,
    GetSnapshotPairsResponse.CurrencyItemModel CurrencyOne,
    GetSnapshotPairsResponse.CurrencyItemModel CurrencyTwo,
    GetSnapshotPairsResponse.PairDataModel CurrencyOneData,
    GetSnapshotPairsResponse.PairDataModel CurrencyTwoData)
  {
    public GetSnapshotPairsResponse(
      SnapshotPair model,
      string? baseCurrencyApiId,
      string? baseCurrencyBaseItemTypeId,
      string baseCurrencyText) : this(
      model.CurrencyExchangeSnapshotPairId,
      model.CurrencyExchangeSnapshotId,
      model.Volume,
      baseCurrencyApiId,
      baseCurrencyBaseItemTypeId,
      baseCurrencyText,
      new CurrencyItemModel(model.CurrencyOne),
      new CurrencyItemModel(model.CurrencyTwo),
      new PairDataModel(model.CurrencyOneData),
      new PairDataModel(model.CurrencyTwoData)) {}

    public record CurrencyItemModel(
      int CurrencyItemId,
      int ItemId,
      int CurrencyCategoryId,
      string? ApiId,
      string? BaseItemTypeId,
      string Text,
      string CategoryApiId,
      string? IconUrl,
      Dictionary<string, object>? ItemMetadata)
    {
      public CurrencyItemModel(CurrencyItem model) : this(
        model.CurrencyItemId,
        model.ItemId,
        model.CurrencyCategoryId,
        model.ApiId,
        model.BaseItemTypeId,
        model.Text,
        model.CategoryApiId,
        model.IconUrl,
        model.ItemMetadata) {}
    }

    public record PairDataModel(
      decimal ValueTraded,
      decimal RelativePrice,
      decimal StockValue,
      long VolumeTraded,
      long HighestStock)
    {
      public PairDataModel(PairData model) : this(
        model.ValueTraded,
        model.RelativePrice,
        model.StockValue,
        model.VolumeTraded,
        model.HighestStock) {}
    }
  }
}
