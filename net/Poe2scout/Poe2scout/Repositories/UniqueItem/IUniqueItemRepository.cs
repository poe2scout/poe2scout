using Poe2scout.Models;
using Poe2scout.Repositories.UniqueItem.Models;

namespace Poe2scout.Repositories.UniqueItem;

public interface IUniqueItemRepository
{
  public Task<int> CreateUniqueItem(CreateUniqueItemModel uniqueItem);
  public Task<IReadOnlyList<Poe2scout.Models.UniqueItem>> GetAllUniqueItems(int gameId);
  public Task<IReadOnlyList<Poe2scout.Models.UniqueItem>> GetCurrentUniqueItems(int gameId);
  public Task<Poe2scout.Models.UniqueItem?> GetUniqueItemByItemId(int itemId, int gameId);
  public Task<int?> GetUniqueItemId(string name);
  public Task<IReadOnlyList<Poe2scout.Models.UniqueItem>> GetUniqueItemsByCategory(string category);
  public Task SetUniqueItemCurrent(int uniqueItemId, bool isCurrent);
  public Task SetUniqueItemMetadata(Dictionary<string, object> itemMetadata, int uniqueItemId);
  public Task UpdateUniqueIconUrl(string iconUrl, int uniqueItemId);
}
