using Dapper;

namespace Poe2scout.Database.Dapper.Repositories.Item;

public partial class ItemRepository
{
    public async Task<IReadOnlyList<Poe2scout.Database.Models.Item>> GetItems() => 
        (await connection.QueryAsync<Poe2scout.Database.Models.Item>(
            """
            SELECT it.value AS name
                ,  it.id AS itemId
              FROM "Item" AS i
              JOIN "BaseItem" AS bi ON i."baseItemId" = bi.id
              JOIN "ItemType" as it ON bi."typeId" = it.id
            """)).AsList();
    
}