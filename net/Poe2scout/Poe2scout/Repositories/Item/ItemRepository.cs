using Dapper;
using System.Data.Common;
using Poe2scout.Repositories.Item.Models;

namespace Poe2scout.Repositories.Item;

public class ItemRepository(DbDataSource dbDataSource) : BaseRepository(dbDataSource), IItemRepository
{
  public async Task<int> CreateBaseItem(CreateBaseItemModel baseItem)
    => await WithConnection(connection =>
    {
      const string query = """
            INSERT INTO base_item (item_type_id, icon_url, item_metadata, game_id)
            VALUES (@ItemTypeId, @IconUrl, @ItemMetadata, @GameId)
            RETURNING base_item_id
""";

      return connection.QuerySingleAsync<int>(
        query,
        new
        {
          baseItem.ItemTypeId,
          baseItem.IconUrl,
          ItemMetadata = ToJson(baseItem.ItemMetadata),
          baseItem.GameId
        });
    });

  public async Task<int> CreateItem(CreateItemModel item)
    => await WithConnection(connection =>
    {
      const string query = """
            INSERT INTO item (base_item_id, item_type)
            VALUES (@BaseItemId, @ItemType)
            RETURNING item_id
""";

      return connection.QuerySingleAsync<int>(query, item);
    });

  public async Task<int> CreateItemCategory(CreateItemCategoryModel itemCategory)
    => await WithConnection(connection =>
    {
      const string query = """
            INSERT INTO item_category (api_id, label, category_kind)
            VALUES (@ApiId, @Label, 'item')
            RETURNING item_category_id
""";

      return connection.QuerySingleAsync<int>(query, itemCategory);
    });

  public async Task<int> CreateItemType(CreateItemTypeModel itemType)
    => await WithConnection(connection =>
    {
      const string query = """
            INSERT INTO item_type (value, item_category_id)
            VALUES (@Value, @ItemCategoryId)
            RETURNING item_type_id
""";

      return connection.QuerySingleAsync<int>(query, itemType);
    });

  public async Task<IReadOnlyList<BaseItem>> GetAllBaseItems(int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT bi.base_item_id
                 , bi.item_type_id
                 , bi.icon_url
                 , bi.item_metadata
                 , bi.game_id
              FROM base_item as bi
             WHERE bi.game_id = @GameId
""";

      return (await connection.QueryAsync<BaseItem>(query, new { GameId = gameId })).AsList();
    });

  public async Task<IReadOnlyList<CategoryIcon>> GetCategoryIcons(int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT gici.item_category_id
                 , ic.api_id
                 , gici.icon_url
              FROM game_item_category_icon AS gici
              JOIN item_category AS ic
                ON ic.item_category_id = gici.item_category_id
             WHERE gici.game_id = @GameId
               AND ic.category_kind = 'item'
             ORDER BY gici.item_category_id
""";

      return (await connection.QueryAsync<CategoryIcon>(query, new { GameId = gameId })).AsList();
    });

  public async Task<IReadOnlyList<ItemCategory>> GetAllItemCategories()
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT item_category_id, api_id, label
              FROM item_category
             WHERE category_kind = 'item'
""";

      return (await connection.QueryAsync<ItemCategory>(query)).AsList();
    });

  public async Task<IReadOnlyList<ItemType>> GetAllItemTypes()
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT item_type_id, value, item_category_id FROM item_type
""";

      return (await connection.QueryAsync<ItemType>(query)).AsList();
    });

  public async Task<IReadOnlyList<Models.Item>> GetAllItems(int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT i.item_id
                 , i.base_item_id
                 , i.item_type
            FROM item i
            JOIN base_item bi ON i.base_item_id = bi.base_item_id
            WHERE bi.game_id = @GameId
""";

      return (await connection.QueryAsync<Models.Item>(query, new { GameId = gameId })).AsList();
    });

  public async Task<IReadOnlyList<ItemCategory>> GetPricedItemCategories(int leagueId, int realmId, int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            WITH priced_categories AS (
                SELECT DISTINCT it.item_category_id
                  FROM item_type AS it
                  JOIN base_item AS bi
                    ON bi.item_type_id = it.item_type_id
                  JOIN item AS i
                    ON i.base_item_id = bi.base_item_id
                  JOIN unique_item AS ui
                    ON ui.item_id = i.item_id
                 WHERE bi.game_id = @GameId
                   AND EXISTS (
                       SELECT 1
                         FROM price_log AS pl
                        WHERE pl.league_id = @LeagueId
                          AND pl.realm_id = @RealmId
                          AND pl.item_id = ui.item_id
                   )
            )
            SELECT ic.item_category_id
                 , ic.api_id
                 , ic.label
             FROM item_category AS ic
             JOIN priced_categories AS pc
               ON pc.item_category_id = ic.item_category_id
            WHERE ic.category_kind = 'item'
             ORDER BY ic.item_category_id
""";

      return (await connection.QueryAsync<ItemCategory>(
        query,
        new { LeagueId = leagueId, RealmId = realmId, GameId = gameId })).AsList();
    });

  public async Task<IReadOnlyList<Models.SearchOption>> GetSearchOptions(int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT
                ui.name AS display_name,
                ic.api_id AS category,
                ui.name AS identifier,
                'unique' AS item_kind
            FROM unique_item ui
            JOIN item i ON ui.item_id = i.item_id
            JOIN base_item bi ON i.base_item_id = bi.base_item_id
            JOIN item_type it ON bi.item_type_id = it.item_type_id
            JOIN item_category ic ON ic.item_category_id = it.item_category_id
            WHERE i.item_type = 'unique'
              AND ic.category_kind = 'item'
              AND bi.game_id = @GameId

            UNION ALL

            SELECT
                ci.text AS display_name,
                cc.api_id AS category,
                ci.text AS identifier,
                'currency' AS item_kind
            FROM currency_item ci
            JOIN item i ON ci.item_id = i.item_id
            JOIN item_category cc ON cc.item_category_id = ci.item_category_id
            JOIN base_item bi ON i.base_item_id = bi.base_item_id
            WHERE i.item_type = 'currency'
              AND bi.game_id = @GameId;
""";

      return (await connection.QueryAsync<Models.SearchOption>(query, new { GameId = gameId })).AsList();
    });
}
