using System.Diagnostics.CodeAnalysis;
using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Uniques;

public static class GetByCategoryHandler
{
  public static async Task<Results<Ok<GetByCategoryResponse>, BadRequest<string>>> GetByCategory(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] ICurrencyItemRepository currencyItemRepository,
    [FromServices] EconomyCache economyCache,
    [FromRoute] string realm,
    [FromRoute] string leagueName,
    [FromQuery] string category,
    [FromQuery] int page = 1,
    [FromQuery] int perPage = 25,
    [FromQuery] int dataPoints = 7,
    [FromQuery] int frequencyHours = 24,
    [FromQuery] string? referenceCurrency = null,
    [FromQuery] string? search = null)
  {
    if (ValidateRequest(page, perPage, dataPoints, frequencyHours, out var errorMessage))
    {
      return TypedResults.BadRequest(errorMessage);
    }

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

    var referenceCurrencyApiId = referenceCurrency ?? league.BaseCurrencyApiId;
    var referenceCurrencyItem = await currencyItemRepository.GetCurrencyItem(referenceCurrencyApiId, validatedRealm.GameId);
    if (referenceCurrencyItem is null)
    {
      return TypedResults.BadRequest("Invalid reference currency.");
    }

    var items = await economyCache.GetUniquePage(
      league.LeagueId,
      validatedRealm.RealmId,
      validatedRealm.GameId,
      category,
      referenceCurrencyApiId,
      dataPoints,
      frequencyHours,
      search);

    var itemCount = items.Count;
    var startingIndex = (page - 1) * perPage;
    var pagedItems = items.Skip(startingIndex).Take(perPage).Select(GetByCategoryResponse.Item.FromModel).ToList();

    return TypedResults.Ok(new GetByCategoryResponse(
      page,
      (int)Math.Ceiling(itemCount / (double)perPage),
      itemCount,
      pagedItems));
  }

  private static bool ValidateRequest(int page, int perPage, int dataPoints, int frequencyHours, [NotNullWhen(true)] out string? errorMessage)
  {
    if (page < 1)
    {
      errorMessage = "Page must be greater than or equal to 1.";

      return true;
    }

    if (perPage is < 1 or > 250)
    {
      errorMessage = "PerPage must be between 1 and 250.";

      return true;
    }

    if (dataPoints is not (7 or 8))
    {
      errorMessage = "DataPoints must be 7 or 8.";

      return true;
    }

    if (frequencyHours is not (1 or 2 or 3 or 4 or 6 or 8 or 12 or 24))
    {
      errorMessage = "FrequencyHours must be one of 1, 2, 3, 4, 6, 8, 12, or 24.";

      return true;
    }

    errorMessage = null;
    return false;
  }

  public record GetByCategoryResponse(int CurrentPage, int Pages, int Total, List<GetByCategoryResponse.Item> Items)
  {
    public record Item(
      int UniqueItemId,
      int ItemId,
      string? IconUrl,
      string Text,
      string Name,
      string CategoryApiId,
      Dictionary<string, object>? ItemMetadata,
      string Type,
      bool? IsChanceable,
      List<Item.PriceLogEntry?> PriceLogs,
      double? CurrentPrice,
      int? CurrentQuantity)
    {
      public record PriceLogEntry(double Price, DateTime Time, int Quantity);

      public static Item FromModel(Models.UniqueItemExtended model) => new(
        model.UniqueItemId,
        model.ItemId,
        model.IconUrl,
        model.Text,
        model.Name,
        model.CategoryApiId,
        model.ItemMetadata,
        model.Type,
        model.IsChanceable,
        model.PriceLogs
          .Select(priceLog => priceLog is null
            ? null
            : new PriceLogEntry(priceLog.Price, priceLog.Time, priceLog.Quantity))
          .ToList(),
        model.CurrentPrice,
        model.CurrentQuantity);
    }
  }
}
