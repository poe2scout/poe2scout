using Dapper;
using Poe2scout.Database.Models;

namespace Poe2scout.Database.Dapper.Repositories.Item;

public partial class ItemRepository
{
    public async Task<IReadOnlyList<ItemCategory>> GetItemCategories() =>
        (await connection.QueryAsync<ItemCategory>(
            """
            SELECT ic.id AS itemCategoryId
                ,  ic."apiId" AS apiId
                ,  ic.label AS label
              FROM "ItemCategory" ic
            """)).AsList();
}