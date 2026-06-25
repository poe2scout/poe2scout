using Poe2scout.Repositories.CurrencyItem.Models;

namespace Poe2scout.Repositories.CurrencyItem;

public interface ICurrencyItemRepository
{
  public Task<int> CreateCurrencyCategory(CreateCurrencyCategoryModel currencyCategory);
  public Task<CreateCurrencyItemResult> CreateCurrencyItem(CreateCurrencyItemModel currencyItem);
  public Task<IReadOnlyList<CurrencyCategory>> GetAllCurrencyCategories();
  public Task<IReadOnlyList<Poe2scout.Models.CurrencyItem>> GetAllCurrencyItems(int gameId);
  public Task<IReadOnlyList<CategoryIcon>> GetCategoryIcons(int gameId);
  public Task<Poe2scout.Models.CurrencyItem?> GetCurrencyItem(string apiId, int gameId);
  public Task<Poe2scout.Models.CurrencyItem> GetDivineItem(int gameId);
  public Task<Poe2scout.Models.CurrencyItem> GetChaosItem(int gameId);
  public Task<Poe2scout.Models.CurrencyItem> GetExaltedItem(int gameId);
  public Task<Poe2scout.Models.CurrencyItem?> GetCurrencyItemByItemId(int itemId, int gameId);
  public Task<IReadOnlyList<Poe2scout.Models.CurrencyItem>> GetCurrencyItems(IReadOnlyList<string> apiIds, int gameId);
  public Task<IReadOnlyList<Poe2scout.Models.CurrencyItem>> GetCurrencyItemsByCategory(string category);
  public Task<IReadOnlyList<CurrencyCategory>> GetPricedCurrencyCategories(int leagueId, int realmId, int gameId);
  public Task<bool> IsItemACurrency(int itemId);
  public Task SetCurrencyItemMetadata(Dictionary<string, object> itemMetadata, int currencyItemId);
  public Task UpdateCurrencyIconUrl(string iconUrl, int currencyItemId);
}
