using Dapper;
using System.Data.Common;
using Poe2scout.Repositories.UniqueItem.Models;

namespace Poe2scout.Repositories.UniqueItem;

public class UniqueItemRepository(DbDataSource dbDataSource) : BaseRepository(dbDataSource), IUniqueItemRepository
{
  public async Task<int> CreateUniqueItem(CreateUniqueItemModel uniqueItem)
    => await WithConnection(connection =>
    {
      const string query = """
            INSERT INTO unique_item (item_id, icon_url, text, name)
            VALUES (@ItemId, @IconUrl, @Text, @Name)
            RETURNING unique_item_id
""";

      return connection.QuerySingleAsync<int>(query, uniqueItem);
    });

  public async Task<IReadOnlyList<Poe2scout.Models.UniqueItem>> GetAllUniqueItems(int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT ui.unique_item_id,
                ui.item_id,
                ui.icon_url,
                ui.text,
                ui.name,
                ic.api_id as category_api_id,
                ui.item_metadata,
                it.value as type,
                ui.is_chanceable,
                ui.is_current
            FROM unique_item as ui
            JOIN item AS i ON ui.item_id = i.item_id
            JOIN base_item AS bi ON i.base_item_id = bi.base_item_id
            JOIN item_type AS it ON bi.item_type_id = it.item_type_id
            JOIN item_category AS ic on ic.item_category_id = it.item_category_id
           WHERE bi.game_id = @GameId
        """;

      return (await connection.QueryAsync<Poe2scout.Models.UniqueItem>(query, new { GameId = gameId })).AsList();
    });

  public async Task<IReadOnlyList<Poe2scout.Models.UniqueItem>> GetCurrentUniqueItems(int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT 
                ui.unique_item_id,
                ui.item_id,
                ui.icon_url,
                ui.text,
                ui.name,
                ic.api_id as category_api_id,
                ui.item_metadata,
                it.value as type,
                ui.is_chanceable,
                ui.is_current
            FROM unique_item as ui
            JOIN item AS i ON ui.item_id = i.item_id
            JOIN base_item AS bi ON i.base_item_id = bi.base_item_id
            JOIN item_type AS it ON bi.item_type_id = it.item_type_id
            JOIN item_category AS ic on ic.item_category_id = it.item_category_id
            WHERE bi.game_id = @GameId
              AND ui.is_current = TRUE
        """;

      return (await connection.QueryAsync<Poe2scout.Models.UniqueItem>(query, new { GameId = gameId })).AsList();
    });

  public async Task<Poe2scout.Models.UniqueItem?> GetUniqueItemByItemId(int itemId, int gameId)
    => await WithConnection(connection =>
    {
      const string query = """
            SELECT ui.unique_item_id,
                ui.item_id,
                ui.icon_url,
                ui.text,
                ui.name,
                ic.api_id AS category_api_id,
                ui.item_metadata,
                it.value AS type,
                ui.is_chanceable,
                ui.is_current
            FROM unique_item AS ui
            JOIN item AS i ON ui.item_id = i.item_id
            JOIN base_item AS bi ON i.base_item_id = bi.base_item_id
            JOIN item_type AS it ON bi.item_type_id = it.item_type_id
            JOIN item_category AS ic ON ic.item_category_id = it.item_category_id
           WHERE ui.item_id = @ItemId
             AND bi.game_id = @GameId
""";

      return connection.QuerySingleOrDefaultAsync<Poe2scout.Models.UniqueItem>(
        query,
        new { ItemId = itemId, GameId = gameId });
    });

  public async Task<int?> GetUniqueItemId(string name)
    => await WithConnection(connection =>
    {
      const string query = """
            SELECT item_id FROM unique_item
            WHERE "name" = @Name
""";

      return connection.QuerySingleOrDefaultAsync<int?>(query, new { Name = name });
    });

  public async Task<IReadOnlyList<Poe2scout.Models.UniqueItem>> GetUniqueItemsByCategory(string category)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT ui.unique_item_id
                , ui.item_id
                , ui.icon_url
                , ui."text"
                , ui."name"
                , ic.api_id as category_api_id
                , ui.item_metadata
                , it."value" as type
                , ui.is_chanceable
                , ui.is_current
            FROM unique_item AS ui
            JOIN item AS i ON ui.item_id = i.item_id
            JOIN base_item AS bi ON i.base_item_id = bi.base_item_id
            JOIN item_type AS it ON bi.item_type_id = it.item_type_id
            JOIN item_category AS ic ON it.item_category_id = ic.item_category_id
            WHERE ic.api_id = @Category
        """;

      return (await connection.QueryAsync<Poe2scout.Models.UniqueItem>(query, new { Category = category })).AsList();
    });

  public async Task SetUniqueItemCurrent(int uniqueItemId, bool isCurrent)
    => await WithConnection(async connection =>
    {
      const string query = """
            UPDATE unique_item
            SET is_current = @IsCurrent
            WHERE unique_item_id = @UniqueItemId
""";

      await connection.ExecuteAsync(query, new { UniqueItemId = uniqueItemId, IsCurrent = isCurrent });
      return true;
    });

  public async Task SetUniqueItemMetadata(Dictionary<string, object> itemMetadata, int uniqueItemId)
    => await WithConnection(async connection =>
    {
      const string query = """
            UPDATE unique_item
            SET item_metadata = @ItemMetadata
            WHERE unique_item_id = @UniqueItemId
""";

      await connection.ExecuteAsync(
        query,
        new { ItemMetadata = ToJson(itemMetadata), UniqueItemId = uniqueItemId });
      return true;
    });

  public async Task UpdateUniqueIconUrl(string iconUrl, int uniqueItemId)
    => await WithConnection(async connection =>
    {
      const string query = """
            UPDATE unique_item
            SET icon_url = @IconUrl
            WHERE unique_item_id = @UniqueItemId
""";

      await connection.ExecuteAsync(query, new { IconUrl = iconUrl, UniqueItemId = uniqueItemId });
      return true;
    });
}
