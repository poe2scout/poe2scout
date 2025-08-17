using System.Data;
using Poe2scout.Database.Models;

namespace Poe2scout.Database.Dapper.Repositories.Item;

public partial class ItemRepository(IDbConnection connection) : IItemRepository
{
    void IDisposable.Dispose()
    {
        connection.Dispose();
        GC.SuppressFinalize(this);
    }
    
    public Task<IReadOnlyList<ItemType>> GetItemTypes()
    {
        throw new NotImplementedException();
    }

    public Task<IReadOnlyList<BaseItem>> GetBaseItems()
    {
        throw new NotImplementedException();
    }

    public Task<IReadOnlyList<CurrencyCategory>> GetCurrencyCategories()
    {
        throw new NotImplementedException();
    }

    public Task<IReadOnlyList<League>> GetLeagues()
    {
        throw new NotImplementedException();
    }
}