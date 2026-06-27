using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.Item;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Items;

public class GetCategoriesHandler
{
  private static readonly HashSet<string> ignoredCurrencyCategories = ["gem", "relics", "waystones"];
  
  public static async Task<Results<Ok<GetCategoriesResponse>, BadRequest<string>>> GetCategories(
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository,
    [FromServices] ICurrencyItemRepository currencyItemRepository,
    [FromServices] IItemRepository itemRepository,
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
    
    var allCurrencyCategoriesTask = currencyItemRepository.GetPricedCurrencyCategories(league.LeagueId, validatedRealm.RealmId, validatedRealm.GameId);
    var allItemCategoriesTask = itemRepository.GetPricedItemCategories(league.LeagueId, validatedRealm.RealmId, validatedRealm.GameId);
    var currencyIconRowsTask = currencyItemRepository.GetCategoryIcons(validatedRealm.GameId);
    var uniqueIconRowsTask = itemRepository.GetCategoryIcons(validatedRealm.GameId);
    
    await Task.WhenAll(allCurrencyCategoriesTask, allItemCategoriesTask, currencyIconRowsTask, uniqueIconRowsTask);
    
    var allCurrencyCategories = allCurrencyCategoriesTask.Result;
    var allItemCategories = allItemCategoriesTask.Result;
    var currencyIconRows = currencyIconRowsTask.Result;
    var uniqueIconRows = uniqueIconRowsTask.Result;

    var currencyIcons = currencyIconRows.ToDictionary(x => x.ApiId, x => x.IconUrl);
    var uniqueIcons = uniqueIconRows.ToDictionary(x => x.ApiId, x => x.IconUrl);

    var uniqueItemCategories =
      allItemCategories.Where(c => c.ApiId != "currency" && !ignoredCurrencyCategories.Contains(c.ApiId)).ToList();
    var currencyItemCategories =
      allCurrencyCategories.Where(c => !ignoredCurrencyCategories.Contains(c.ApiId)).ToList();
    
    return TypedResults.Ok(new GetCategoriesResponse(uniqueItemCategories, currencyItemCategories, uniqueIcons, currencyIcons));
  }

  public record GetCategoriesResponse(List<GetCategoriesResponse.ItemCategory> UniqueCategories, List<GetCategoriesResponse.CurrencyCategory> CurrencyCategories)
  {
    public GetCategoriesResponse(List<Repositories.Item.Models.ItemCategory> ics, List<Repositories.CurrencyItem.Models.CurrencyCategory> ccs, Dictionary<string, string> uil, Dictionary<string, string> cil) : this(
      UniqueCategories: ics.Select(uc => new ItemCategory(uc, uil)).ToList(),
      CurrencyCategories: ccs.Select(cc => new CurrencyCategory(cc, cil)).ToList()) {}

    public record ItemCategory(int ItemCategoryId, string ApiId, string Label, string Icon)
    {
      public ItemCategory(Repositories.Item.Models.ItemCategory m, Dictionary<string, string> il) : this(
        ItemCategoryId: m.ItemCategoryId,
        ApiId: m.ApiId,
        Label: m.Label,
        Icon: il[m.ApiId]) {}
    }

    public record CurrencyCategory(int CurrencyCategoryId, string ApiId, string Label, string Icon)
    {
      public CurrencyCategory(Repositories.CurrencyItem.Models.CurrencyCategory cc, Dictionary<string, string> cl) : this(
        CurrencyCategoryId: cc.CurrencyCategoryId,
        ApiId: cc.ApiId,
        Label: cc.Label,
        Icon: cl[cc.ApiId]) {}
    }
  }
}