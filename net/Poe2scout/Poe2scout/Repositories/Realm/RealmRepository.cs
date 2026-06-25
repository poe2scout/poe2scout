using Dapper;
using System.Data.Common;

namespace Poe2scout.Repositories.Realm;

public class RealmRepository(DbDataSource dbDataSource) : BaseRepository(dbDataSource), IRealmRepository
{
  public async Task<Models.Realm?> GetRealm(string apiId)
    => await WithConnection(connection =>
    {
      const string query = """
SELECT realm_id
     , game_id
  FROM realm
 WHERE api_id = @ApiId;
""";

      return connection.QuerySingleOrDefaultAsync<Models.Realm>(query, new { ApiId = apiId });
    });

  public async Task<IReadOnlyList<Models.Realm>> GetRealms()
    => await WithConnection(async connection =>
    {
      const string query = """
SELECT realm_id
     , game_id
     , api_id
  FROM realm;
""";

      return (await connection.QueryAsync<Models.Realm>(query)).AsList();
    });
}
