using Dapper;
using Poe2scout.Database.Models;

namespace Poe2scout.Database.Dapper.Repositories.Item;

public partial class ItemRepository
{
    public async Task<IReadOnlyList<CurrencyItem>> GetCurrencyItems() =>
        (await connection.QueryAsync<CurrencyItem>(
            """
            SELECT i.id AS itemId
                ,  ci."apiId" AS apiId
                ,  ci.text AS text
                ,  cc."apiId" AS currencyCategoryApiId
                ,  ci."iconUrl" AS iconUrl
                ,  ci."itemMetadata" AS itemMetadata
                ,  it."value" as itemTypeName
              FROM "CurrencyItem" AS ci
              JOIN "CurrencyCategory" AS cc ON cc.id = ci."currencyCategoryId"
              JOIN "Item" AS i ON ci."itemId" = i.id
              JOIN "BaseItem" AS bi ON i."baseItemId" = bi.id
              JOIN "ItemType" AS it ON it.id = bi."typeId"
            """)).AsList();
}