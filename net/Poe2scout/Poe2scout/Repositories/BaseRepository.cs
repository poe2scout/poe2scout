using System.Data;
using System.Data.Common;
using System.Text.Json;
using Dapper;

namespace Poe2scout.Repositories;

public class BaseRepository(DbDataSource dbDataSource)
{
  static BaseRepository()
  {
    DefaultTypeMap.MatchNamesWithUnderscores = true;
    SqlMapper.AddTypeHandler(new DictionaryJsonTypeHandler());
    SqlMapper.RemoveTypeMap(typeof(DateTime));
    SqlMapper.RemoveTypeMap(typeof(DateTime?));
    SqlMapper.AddTypeHandler(new UtcDateTimeTypeHandler());
  }

  protected async Task<T> WithConnection<T>(Func<IDbConnection, Task<T>> action)
  {
    await using var connection = await dbDataSource.OpenConnectionAsync();
    
    return await action(connection);
  }

  protected async Task<T> WithTransaction<T>(Func<IDbTransaction, Task<T>> action)
  {
    await using var connection = await dbDataSource.OpenConnectionAsync();
    
    await using var transaction = await connection.BeginTransactionAsync();

    try
    {
      var result = await action(transaction);
      await transaction.CommitAsync();

      return result;
    }
    catch
    {
      await transaction.RollbackAsync();

      throw;
    }
  }

  protected static string? ToJson(Dictionary<string, object>? value)
    => value is null ? null : JsonSerializer.Serialize(value);
}
