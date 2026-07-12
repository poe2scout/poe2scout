using Poe2scout.Repositories.Item.Models;

namespace Poe2scout.Repositories.Item;

public interface IItemRepository
{
  public Task<int> CreateBaseItem(CreateBaseItemModel baseItem);
  public Task<int> CreateItem(CreateItemModel item);
  public Task<int> CreateItemCategory(CreateItemCategoryModel itemCategory);
  public Task<int> CreateItemType(CreateItemTypeModel itemType);
  public Task<IReadOnlyList<BaseItem>> GetAllBaseItems(int gameId);
  public Task<IReadOnlyList<CategoryIcon>> GetCategoryIcons(int gameId);
  public Task<IReadOnlyList<ItemCategory>> GetAllItemCategories();
  public Task<IReadOnlyList<ItemType>> GetAllItemTypes();
  public Task<IReadOnlyList<Models.Item>> GetAllItems(int gameId);
  public Task<IReadOnlyList<ItemCategory>> GetPricedItemCategories(int leagueId, int realmId, int gameId);
  public Task<IReadOnlyList<Models.SearchOption>> GetSearchOptions(int gameId);
}
