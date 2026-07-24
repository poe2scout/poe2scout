using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Repositories.CurrencyExchange;
using Poe2scout.Repositories.CurrencyExchange.Models;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Currencies;

public static class GetPairHistoryHandler
{
  public static void MapGet(IEndpointRouteBuilder app)
  {
    app.MapGet("/{realm}/Leagues/{leagueName}/Currencies/Pairs/{currencyOneItemId:int}/{currencyTwoItemId:int}/History", GetPairHistory);
  }

  private static async Task<Results<Ok<GetPairHistoryResponse>, BadRequest<string>>> GetPairHistory(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] ICurrencyExchangeRepository currencyExchangeRepository,
    [FromRoute] string realm,
    [FromRoute] string leagueName,
    [FromRoute] int currencyOneItemId,
    [FromRoute] int currencyTwoItemId,
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

    var pairHistory = await currencyExchangeRepository.GetPairHistory(
      league.LeagueId, 
      validatedRealm.RealmId,
      currencyOneItemId,
      currencyTwoItemId,
      endEpoch ?? (int)new DateTimeOffset(DateTime.UtcNow).ToUnixTimeSeconds(),
      limit);
    
    return TypedResults.Ok(new GetPairHistoryResponse(
      pairHistory,
      league.BaseCurrencyApiId,
      league.BaseCurrencyBaseItemTypeId,
      league.BaseCurrencyText));
  }

  public record GetPairHistoryResponse(
    IEnumerable<GetPairHistoryResponse.Pair> History,
    GetPairHistoryResponse.MetaModel Meta,
    string? BaseCurrencyApiId,
    string? BaseCurrencyBaseItemTypeId,
    string BaseCurrencyText)
  {
    public GetPairHistoryResponse(
      PairHistory pairHistory,
      string? baseCurrencyApiId,
      string? baseCurrencyBaseItemTypeId,
      string baseCurrencyText) : this(
      History: pairHistory.History.Select(h => new Pair(h)),
      Meta: new MetaModel(HasMore: pairHistory.Meta.TryGetValue("has_more", out var hasMore) && (bool)hasMore),
      BaseCurrencyApiId: baseCurrencyApiId,
      BaseCurrencyBaseItemTypeId: baseCurrencyBaseItemTypeId,
      BaseCurrencyText: baseCurrencyText) {} 
    public record MetaModel(bool HasMore);
    
    public record Pair(int Epoch, Pair.DataModel Data)
    {
      public Pair(PairHistoryEntry m) : this(
        Epoch: m.Epoch,
        Data: new DataModel(m.Data)) { }
      
      public record DataModel(DataModel.Details CurrencyOneData, DataModel.Details CurrencyTwoData)
      {
        public DataModel(PairHistoryEntryData m) : this(
          CurrencyOneData: new Details(m.CurrencyOneData),
          CurrencyTwoData: new Details(m.CurrencyTwoData)) { }
        
        public record Details(
          int CurrencyItemId,
          decimal ValueTraded,
          decimal RelativePrice,
          decimal StockValue,
          long VolumeTraded,
          long HighestStock)
        {
          public Details(PairHistoryEntryDataDetails m) : this(
            m.CurrencyItemId,
            m.ValueTraded,
            m.RelativePrice,
            m.StockValue,
            m.VolumeTraded,
            m.HighestStock) { }
        }
      }
    }
  }
}
