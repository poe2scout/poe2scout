using Poe2scout.Database.Models;

namespace Poe2scout.Database;

public interface IItemRepository: IDisposable
{
    public Task<IReadOnlyList<Item>> GetItems();
    public Task<IReadOnlyList<UniqueItem>> GetUniqueItems();
    public Task<IReadOnlyList<CurrencyItem>> GetCurrencyItems();
    public Task<IReadOnlyList<ItemType>> GetItemTypes();
    public Task<IReadOnlyList<ItemCategory>> GetItemCategories();
    public Task<IReadOnlyList<BaseItem>> GetBaseItems();
    public Task<IReadOnlyList<CurrencyCategory>> GetCurrencyCategories();
    public Task<IReadOnlyList<League>> GetLeagues();
}