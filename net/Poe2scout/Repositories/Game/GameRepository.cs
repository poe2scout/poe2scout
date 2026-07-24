using Dapper;
using System.Data.Common;
using Poe2scout.Repositories.Game.Models;

namespace Poe2scout.Repositories.Game;

public class GameRepository(DbDataSource dbDataSource) : BaseRepository(dbDataSource), IGameRepository
{
  public async Task<IReadOnlyList<BridgeCurrency>> GetBridgeCurrencies(int gameId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT ci.item_id,
                   ci.currency_item_id,
                   ci.api_id,
                   ci.base_item_type_id,
                   ci.text,
                   ci.icon_url,
                   gcb.bridge_rank
              FROM game_currency_bridge AS gcb
              JOIN currency_item AS ci
                ON ci.currency_item_id = gcb.currency_item_id
              JOIN item AS i
                ON i.item_id = ci.item_id
              JOIN base_item AS bi
                ON bi.base_item_id = i.base_item_id
             WHERE gcb.game_id = @GameId
               AND bi.game_id = @GameId
             ORDER BY gcb.bridge_rank ASC
""";

      return (await connection.QueryAsync<BridgeCurrency>(query, new { GameId = gameId })).AsList();
    });

  public async Task<int> GetDefaultLeague(int gameId)
    => await WithConnection(connection =>
    {
      const string query = """
SELECT default_league_id
  FROM game
 WHERE game_id = @GameId;
""";

      return connection.QuerySingleAsync<int>(query, new { GameId = gameId });
    });

  public async Task<IReadOnlyList<Models.Game>> GetGames()
    => await WithConnection(async connection =>
    {
      const string query = """
SELECT game_id
     , api_id
     , label
     , ggg_api_trade_identifier
     , default_league_id
  FROM game;
""";

      return (await connection.QueryAsync<Models.Game>(query)).AsList();
    });
}
