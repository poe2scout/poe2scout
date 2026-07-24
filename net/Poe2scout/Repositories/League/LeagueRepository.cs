using Dapper;
using System.Data.Common;

namespace Poe2scout.Repositories.League;

public class LeagueRepository(DbDataSource dbDataSource) : BaseRepository(dbDataSource), ILeagueRepository
{
  public async Task<IReadOnlyList<int>> GetItemsInCurrentLeague(int leagueId, int realmId)
    => await WithConnection(async connection =>
    {
      const string query = """
WITH RECURSIVE distinct_items AS (
    (
        SELECT item_id 
        FROM price_log 
        WHERE league_id = @LeagueId AND realm_id = @RealmId 
        ORDER BY item_id 
        LIMIT 1
    )
    UNION ALL
    SELECT (
        SELECT item_id 
        FROM price_log 
        WHERE league_id = @LeagueId AND realm_id = @RealmId
          AND item_id > distinct_items.item_id 
        ORDER BY item_id 
        LIMIT 1
    )
    FROM distinct_items
    WHERE distinct_items.item_id IS NOT NULL
)
SELECT item_id 
FROM distinct_items
WHERE item_id IS NOT NULL
""";

      return (await connection.QueryAsync<int>(query, new { LeagueId = leagueId, RealmId = realmId })).AsList();
    });

  public async Task<Models.League?> GetLeagueByValue(string value, int gameId)
    => await WithConnection(connection =>
    {
      const string query = """
            SELECT l.league_id,
                   l.value,
                   l.short_name,
                   l.base_currency_item_id,
                   ci.api_id AS base_currency_api_id,
                   ci.base_item_type_id AS base_currency_base_item_type_id,
                   ci.text AS base_currency_text,
                   ci.icon_url AS base_currency_icon_url,
                   l.current_league
              FROM league AS l
              JOIN currency_item AS ci
                ON ci.item_id = l.base_currency_item_id
             WHERE (l.value ILIKE @Value OR l.short_name ILIKE @Value)
               AND l.game_id = @GameId
""";

      return connection.QuerySingleOrDefaultAsync<Models.League>(query, new { Value = value, GameId = gameId });
    });

  public async Task<IReadOnlyList<Models.League>> GetLeagues(int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT l.league_id,
                   l.value,
                   l.short_name,
                   l.base_currency_item_id,
                   ci.api_id AS base_currency_api_id,
                   ci.base_item_type_id AS base_currency_base_item_type_id,
                   ci.text AS base_currency_text,
                   ci.icon_url AS base_currency_icon_url,
                   l.current_league
              FROM league AS l
              JOIN currency_item AS ci
                ON ci.item_id = l.base_currency_item_id
             WHERE l.game_id = @GameId
""";

      return (await connection.QueryAsync<Models.League>(query, new { GameId = gameId })).AsList();
    });

  public async Task<IReadOnlyList<Models.League>> GetCurrentLeagues(int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT l.league_id,
                   l.value,
                   l.short_name,
                   l.base_currency_item_id,
                   ci.api_id AS base_currency_api_id,
                   ci.base_item_type_id AS base_currency_base_item_type_id,
                   ci.text AS base_currency_text,
                   ci.icon_url AS base_currency_icon_url,
                   l.current_league
              FROM league AS l
              JOIN currency_item AS ci
                ON ci.item_id = l.base_currency_item_id
            WHERE current_league = true
              AND game_id = @GameId
""";

      return (await connection.QueryAsync<Models.League>(query, new { GameId = gameId })).AsList();
    });

  public async Task<Models.League> GetLeague(int leagueId)
    => await WithConnection(connection =>
    {
      const string query = """
            SELECT l.league_id,
                   l.value,
                   l.short_name,
                   l.base_currency_item_id,
                   ci.api_id AS base_currency_api_id,
                   ci.base_item_type_id AS base_currency_base_item_type_id,
                   ci.text AS base_currency_text,
                   ci.icon_url AS base_currency_icon_url,
                   l.current_league
              FROM league AS l
              JOIN currency_item AS ci
                ON ci.item_id = l.base_currency_item_id
             WHERE l.league_id = @LeagueId
""";

      return connection.QuerySingleAsync<Models.League>(query, new { LeagueId = leagueId });
    });
}
