using Dapper;
using Poe2scout.Database.Models;

namespace Poe2scout.Database.Dapper.Repositories.Item;

public partial class ItemRepository
{
    public async Task<IReadOnlyList<UniqueItem>> GetUniqueItems() =>
        (await connection.QueryAsync<UniqueItem>(
            """
            SELECT i.id AS itemId
                ,  ui."iconUrl" AS iconUrl
                ,  ui."name" AS name
                ,  ui."text" AS text
                ,  ui."itemMetadata" AS itemMetadata
                ,  ui."isChanceable" AS isChanceable
                ,  ic."apiId" AS categoryApiId
                ,  it.value AS itemTypeName
              FROM "UniqueItem" AS ui
              JOIN "Item" AS i ON ui."itemId" = i.id
              JOIN "BaseItem" AS bi ON i."baseItemId" = bi.id
              JOIN "ItemType" AS it ON it.id = bi."typeId"
              JOIN "ItemCategory" AS ic ON ic.id = it."categoryId"
            """)).AsList();
}