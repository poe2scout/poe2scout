using System.Data;
using System.Data.Common;

namespace Poe2scout.Repositories;

public class BaseRepository(DbDataSource dbDataSource)
{
  public async Task<T> WithConnection<T>(Func<IDbConnection, Task<T>> action)
  {
    await using var connection = await dbDataSource.OpenConnectionAsync();
    
    return await action(connection);
  }

  public async Task<T> WithTransaction<T>(Func<IDbTransaction, Task<T>> action)
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
}