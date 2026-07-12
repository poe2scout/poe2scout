using Dapper;
using System.Data.Common;
using Poe2scout.Repositories.CurrencyItem.Models;

namespace Poe2scout.Repositories.CurrencyItem;

public class CurrencyItemRepository(DbDataSource dbDataSource) : BaseRepository(dbDataSource), ICurrencyItemRepository
{
  public async Task<int> CreateCurrencyCategory(CreateCurrencyCategoryModel currencyCategory)
    => await WithConnection(connection =>
    {
      const string query = """
            INSERT INTO item_category (api_id, label, category_kind)
            VALUES (@ApiId, @Label, 'currency')
            RETURNING item_category_id
""";

      return connection.QuerySingleAsync<int>(query, currencyCategory);
    });

  public async Task<CreateCurrencyItemResult> CreateCurrencyItem(CreateCurrencyItemModel currencyItem)
    => await WithConnection(async connection =>
    {
      const string validationQuery = """
            SELECT EXISTS(
                SELECT 1
                  FROM item_category
                 WHERE item_category_id = @ItemCategoryId
                   AND category_kind = 'currency'
            )
""";

      var isValidCategory = await connection.QuerySingleAsync<bool>(
        validationQuery,
        new { currencyItem.ItemCategoryId });

      if (!isValidCategory)
      {
        return new CreateCurrencyItemResult(false, null, CreateCurrencyItemError.InvalidCategoryKind);
      }

      const string insertQuery = """
            INSERT INTO currency_item (item_id, item_category_id, api_id, text, icon_url)
            VALUES (@ItemId, @ItemCategoryId, @ApiId, @Text, @Image)
            RETURNING currency_item_id
""";

      var currencyItemId = await connection.QuerySingleAsync<int>(insertQuery, currencyItem);
      return new CreateCurrencyItemResult(true, currencyItemId, null);
    });

  public async Task<IReadOnlyList<CurrencyCategory>> GetAllCurrencyCategories()
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT item_category_id AS currency_category_id
                 , api_id
                 , label
              FROM item_category
             WHERE category_kind = 'currency'
""";

      return (await connection.QueryAsync<CurrencyCategory>(query)).AsList();
    });

  public async Task<IReadOnlyList<Poe2scout.Models.CurrencyItem>> GetAllCurrencyItems(int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT ci.currency_item_id
                 , ci.item_id
                 , ci.item_category_id AS currency_category_id
                 , ci.api_id
                 , ci.text
                 , cc.api_id as category_api_id
                 , ci.icon_url
                 , ci.item_metadata
              FROM currency_item as ci
              JOIN item_category as cc on ci.item_category_id = cc.item_category_id
              JOIN item as i ON ci.item_id = i.item_id
              JOIN base_item as bi ON bi.base_item_id = i.base_item_id
             WHERE bi.game_id = @GameId
""";

      return (await connection.QueryAsync<Poe2scout.Models.CurrencyItem>(query, new { GameId = gameId })).AsList();
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
               AND ic.category_kind = 'currency'
             ORDER BY gici.item_category_id
""";

      return (await connection.QueryAsync<CategoryIcon>(query, new { GameId = gameId })).AsList();
    });

  public async Task<Poe2scout.Models.CurrencyItem?> GetCurrencyItem(string apiId, int gameId)
    => await WithConnection(connection =>
    {
      const string query = """
            SELECT ci.currency_item_id,
                ci.item_id,
                ci.item_category_id AS currency_category_id,
                ci.api_id,
                ci.text,
                cc.api_id as category_api_id,
                ci.icon_url,
                ci.item_metadata
            FROM currency_item as ci
            JOIN item_category as cc on ci.item_category_id = cc.item_category_id
            JOIN item AS i ON i.item_id = ci.item_id
            JOIN base_item AS bi ON bi.base_item_id = i.base_item_id
            WHERE ci.api_id = @ApiId
              AND bi.game_id = @GameId
""";

      return connection.QuerySingleOrDefaultAsync<Poe2scout.Models.CurrencyItem>(
        query,
        new { ApiId = apiId, GameId = gameId });
    });

  public async Task<Poe2scout.Models.CurrencyItem> GetDivineItem(int gameId)
    => await GetCurrencyItem("divine", gameId) ?? throw new InvalidOperationException("Divine item was not found");

  public async Task<Poe2scout.Models.CurrencyItem> GetChaosItem(int gameId)
    => await GetCurrencyItem("chaos", gameId) ?? throw new InvalidOperationException("Chaos item was not found");

  public async Task<Poe2scout.Models.CurrencyItem> GetExaltedItem(int gameId)
    => await GetCurrencyItem("exalted", gameId) ?? throw new InvalidOperationException("Exalted item was not found");

  public async Task<Poe2scout.Models.CurrencyItem?> GetCurrencyItemByItemId(int itemId, int gameId)
    => await WithConnection(connection =>
    {
      const string query = """
            SELECT ci.currency_item_id,
                ci.item_id,
                ci.item_category_id AS currency_category_id,
                ci.api_id,
                ci.text,
                cc.api_id AS category_api_id,
                ci.icon_url,
                ci.item_metadata
            FROM currency_item AS ci
            JOIN item_category AS cc ON ci.item_category_id = cc.item_category_id
            JOIN item AS i ON i.item_id = ci.item_id
            JOIN base_item AS bi ON bi.base_item_id = i.base_item_id
           WHERE ci.item_id = @ItemId
             AND bi.game_id = @GameId
""";

      return connection.QuerySingleOrDefaultAsync<Poe2scout.Models.CurrencyItem>(
        query,
        new { ItemId = itemId, GameId = gameId });
    });

  public async Task<IReadOnlyList<Poe2scout.Models.CurrencyItem>> GetCurrencyItems(List<string> apiIds, int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
SELECT ci.currency_item_id
    , ci.item_id
    , ci.item_category_id AS currency_category_id
    , ci.api_id
    , ci.text
    , cc.api_id AS category_api_id
    , ci.icon_url
    , ci.item_metadata
FROM currency_item AS ci
JOIN item_category AS cc ON ci.item_category_id = cc.item_category_id
JOIN item AS i ON ci.item_id = i.item_id
JOIN base_item AS bi ON i.base_item_id = bi.base_item_id
WHERE ci.api_id = ANY(@ApiIds)
  AND bi.game_id = @GameId
""";

      return (await connection.QueryAsync<Poe2scout.Models.CurrencyItem>(
        query,
        new { ApiIds = apiIds.ToArray(), GameId = gameId })).AsList();
    });

  public async Task<IReadOnlyList<Poe2scout.Models.CurrencyItem>> GetCurrencyItemsByCategory(string category)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT ci.currency_item_id
                , ci.item_id
                , ci.item_category_id AS currency_category_id
                , ci.api_id
                , ci.text
                , cc.api_id as category_api_id
                , ci.icon_url
                , ci.item_metadata
            FROM currency_item AS ci
            JOIN item_category AS cc ON ci.item_category_id = cc.item_category_id
            WHERE cc.api_id ILIKE @Category
""";

      return (await connection.QueryAsync<Poe2scout.Models.CurrencyItem>(query, new { Category = category })).AsList();
    });

  public async Task<IReadOnlyList<CurrencyCategory>> GetPricedCurrencyCategories(int leagueId, int realmId, int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            WITH priced_items AS (
                SELECT DISTINCT ci.item_category_id
                  FROM currency_item AS ci
                  JOIN item AS i
                    ON i.item_id = ci.item_id
                  JOIN base_item AS bi
                    ON bi.base_item_id = i.base_item_id
                 WHERE bi.game_id = @GameId
                   AND EXISTS (
                       SELECT 1
                         FROM price_log AS pl
                        WHERE pl.league_id = @LeagueId
                          AND pl.realm_id = @RealmId
                          AND pl.item_id = ci.item_id
                   )
            )
            SELECT cc.item_category_id AS currency_category_id
                 , cc.api_id
                 , cc.label
             FROM item_category AS cc
             JOIN priced_items AS pi ON pi.item_category_id = cc.item_category_id
             ORDER BY cc.item_category_id
""";

      return (await connection.QueryAsync<CurrencyCategory>(
        query,
        new { LeagueId = leagueId, RealmId = realmId, GameId = gameId })).AsList();
    });

  public async Task<bool> IsItemACurrency(int itemId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT 1
            FROM currency_item as ci
            WHERE ci.item_id = @ItemId
""";

      var rows = await connection.QueryAsync<int>(query, new { ItemId = itemId });
      return rows.Count() == 1;
    });

  public async Task SetCurrencyItemMetadata(Dictionary<string, object> itemMetadata, int currencyItemId)
    => await WithConnection(async connection =>
    {
      const string query = """
            UPDATE currency_item
            SET item_metadata = @ItemMetadata
            WHERE currency_item_id = @CurrencyItemId
""";

      await connection.ExecuteAsync(
        query,
        new { ItemMetadata = ToJson(itemMetadata), CurrencyItemId = currencyItemId });
      return true;
    });

  public async Task UpdateCurrencyIconUrl(string iconUrl, int currencyItemId)
    => await WithConnection(async connection =>
    {
      const string query = """
            UPDATE currency_item
            SET icon_url = @IconUrl
            WHERE currency_item_id = @CurrencyItemId
""";

      await connection.ExecuteAsync(query, new { IconUrl = iconUrl, CurrencyItemId = currencyItemId });
      return true;
    });
}
