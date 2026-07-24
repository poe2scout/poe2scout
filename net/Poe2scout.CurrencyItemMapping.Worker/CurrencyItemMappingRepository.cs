using System.Data.Common;
using Dapper;

namespace Poe2scout.CurrencyItemMapping.Worker;

public interface ICurrencyItemMappingRepository
{
  Task<IReadOnlyList<MappingCurrencyRow>> GetCurrencies();

  Task Apply(
    IReadOnlyList<GameMappingReport> reports,
    IReadOnlyList<ConfirmedAlias> aliases);
}

public sealed class CurrencyItemMappingRepository(
  DbDataSource dbDataSource,
  CurrencyItemMappingConfig config) : ICurrencyItemMappingRepository
{
  public async Task<IReadOnlyList<MappingCurrencyRow>> GetCurrencies()
  {
    const string query = """
SELECT
    g.game_id,
    g.api_id AS game_api_id,
    ci.currency_item_id,
    ci.item_id,
    ci.api_id,
    ci.base_item_type_id,
    ci.text
FROM currency_item ci
JOIN item i ON i.item_id = ci.item_id
JOIN base_item bi ON bi.base_item_id = i.base_item_id
JOIN game g ON g.game_id = bi.game_id
ORDER BY g.game_id, ci.currency_item_id;
""";

    await using var connection = await dbDataSource.OpenConnectionAsync();
    return (await connection.QueryAsync<MappingCurrencyRow>(query)).AsList();
  }

  public async Task Apply(
    IReadOnlyList<GameMappingReport> reports,
    IReadOnlyList<ConfirmedAlias> aliases)
  {
    await using var connection = await dbDataSource.OpenConnectionAsync();
    await using var transaction = await connection.BeginTransactionAsync();
    try
    {
      foreach (var alias in aliases)
      {
        await MergeAlias(
          connection,
          transaction,
          alias,
          config.ApplyCommandTimeoutSeconds);
      }

      const string updateMapping = """
UPDATE currency_item
SET base_item_type_id = @BaseItemTypeId
WHERE currency_item_id = @CurrencyItemId;
""";
      foreach (var assignment in reports
                 .SelectMany(report => report.Assignments)
                 .Where(assignment => !assignment.IsUnchanged))
      {
        var changed = await connection.ExecuteAsync(
          updateMapping,
          new { assignment.CurrencyItemId, assignment.BaseItemTypeId },
          transaction,
          commandTimeout: config.ApplyCommandTimeoutSeconds);
        if (changed != 1)
        {
          throw new InvalidOperationException(
            $"Currency item {assignment.CurrencyItemId} disappeared while applying mappings.");
        }
      }

      const string clearTattooCopy = """
UPDATE currency_item
SET base_item_type_id = NULL
WHERE api_id = 'loyalty-tattoo-of-ikiahoCopy';
""";
      await connection.ExecuteAsync(
        clearTattooCopy,
        transaction: transaction,
        commandTimeout: config.ApplyCommandTimeoutSeconds);

      const string duplicateMappings = """
SELECT COUNT(*)
FROM (
    SELECT bi.game_id, ci.base_item_type_id
    FROM currency_item ci
    JOIN item i ON i.item_id = ci.item_id
    JOIN base_item bi ON bi.base_item_id = i.base_item_id
    WHERE ci.base_item_type_id IS NOT NULL
    GROUP BY bi.game_id, ci.base_item_type_id
    HAVING COUNT(*) > 1
) duplicates;
""";
      if (await connection.ExecuteScalarAsync<int>(
            duplicateMappings,
            transaction: transaction,
            commandTimeout: config.ApplyCommandTimeoutSeconds) != 0)
      {
        throw new InvalidOperationException(
          "Applying mappings would assign a base item type ID to multiple currencies in one game.");
      }

      await transaction.CommitAsync();
    }
    catch
    {
      await transaction.RollbackAsync();
      throw;
    }
  }

  private static async Task MergeAlias(
    DbConnection connection,
    DbTransaction transaction,
    ConfirmedAlias alias,
    int commandTimeout)
  {
    const string selectRows = """
SELECT
    ci.currency_item_id,
    ci.item_id,
    i.base_item_id,
    bi.item_type_id,
    ci.api_id
FROM currency_item ci
JOIN item i ON i.item_id = ci.item_id
JOIN base_item bi ON bi.base_item_id = i.base_item_id
JOIN game g ON g.game_id = bi.game_id
WHERE g.api_id = @GameApiId
  AND ci.api_id IN (@RetiredApiId, @CanonicalApiId)
FOR UPDATE;
""";
    var rows = (await connection.QueryAsync<AliasRow>(
      selectRows,
      alias,
      transaction,
      commandTimeout: commandTimeout)).AsList();
    var retired = rows.SingleOrDefault(row => row.ApiId == alias.RetiredApiId);
    if (retired is null)
    {
      return;
    }

    var canonical = rows.SingleOrDefault(row => row.ApiId == alias.CanonicalApiId)
                    ?? throw new InvalidOperationException(
                      $"Canonical alias target {alias.GameApiId}:{alias.CanonicalApiId} is missing.");

    var ids = new
    {
      RetiredItemId = retired.ItemId,
      RetiredCurrencyItemId = retired.CurrencyItemId,
      RetiredBaseItemId = retired.BaseItemId,
      RetiredItemTypeId = retired.ItemTypeId,
      CanonicalItemId = canonical.ItemId,
      CanonicalCurrencyItemId = canonical.CurrencyItemId
    };

    const string pairConflict = """
WITH affected AS (
    SELECT
        currency_exchange_snapshot_pair_id,
        currency_exchange_snapshot_id,
        LEAST(
          CASE WHEN currency_one_item_id = @RetiredItemId THEN @CanonicalItemId ELSE currency_one_item_id END,
          CASE WHEN currency_two_item_id = @RetiredItemId THEN @CanonicalItemId ELSE currency_two_item_id END
        ) AS item_one,
        GREATEST(
          CASE WHEN currency_one_item_id = @RetiredItemId THEN @CanonicalItemId ELSE currency_one_item_id END,
          CASE WHEN currency_two_item_id = @RetiredItemId THEN @CanonicalItemId ELSE currency_two_item_id END
        ) AS item_two
    FROM currency_exchange_snapshot_pair
    WHERE currency_one_item_id = @RetiredItemId
       OR currency_two_item_id = @RetiredItemId
)
SELECT COUNT(*)
FROM affected
WHERE item_one = item_two
   OR EXISTS (
       SELECT 1
       FROM currency_exchange_snapshot_pair other
       WHERE other.currency_exchange_snapshot_id = affected.currency_exchange_snapshot_id
         AND other.currency_exchange_snapshot_pair_id <> affected.currency_exchange_snapshot_pair_id
         AND LEAST(
               CASE WHEN other.currency_one_item_id = @RetiredItemId THEN @CanonicalItemId ELSE other.currency_one_item_id END,
               CASE WHEN other.currency_two_item_id = @RetiredItemId THEN @CanonicalItemId ELSE other.currency_two_item_id END
             ) = affected.item_one
         AND GREATEST(
               CASE WHEN other.currency_one_item_id = @RetiredItemId THEN @CanonicalItemId ELSE other.currency_one_item_id END,
               CASE WHEN other.currency_two_item_id = @RetiredItemId THEN @CanonicalItemId ELSE other.currency_two_item_id END
             ) = affected.item_two
   );
""";
    if (await connection.ExecuteScalarAsync<int>(
          pairConflict,
          ids,
          transaction,
          commandTimeout: commandTimeout) != 0)
    {
      throw new InvalidOperationException(
        $"Alias merge {alias.RetiredApiId} -> {alias.CanonicalApiId} would create a self-pair or duplicate pair.");
    }

    const string pairDataConflict = """
SELECT COUNT(*)
FROM currency_exchange_snapshot_pair_data retired
JOIN currency_exchange_snapshot_pair_data canonical
  ON canonical.currency_exchange_snapshot_pair_id =
     retired.currency_exchange_snapshot_pair_id
 AND canonical.item_id = @CanonicalItemId
WHERE retired.item_id = @RetiredItemId;
""";
    if (await connection.ExecuteScalarAsync<int>(
          pairDataConflict,
          ids,
          transaction,
          commandTimeout: commandTimeout) != 0)
    {
      throw new InvalidOperationException(
        $"Alias merge {alias.RetiredApiId} -> {alias.CanonicalApiId} would duplicate pair data.");
    }

    const string mergeSql = """
DELETE FROM item_daily_stats
WHERE item_id IN (@RetiredItemId, @CanonicalItemId);

DELETE FROM price_log retired
USING price_log canonical
WHERE retired.item_id = @RetiredItemId
  AND canonical.item_id = @CanonicalItemId
  AND retired.realm_id = canonical.realm_id
  AND retired.league_id = canonical.league_id
  AND retired.created_at = canonical.created_at;

UPDATE price_log
SET item_id = @CanonicalItemId
WHERE item_id = @RetiredItemId;

UPDATE currency_exchange_snapshot_pair_data
SET item_id = @CanonicalItemId
WHERE item_id = @RetiredItemId;

UPDATE currency_exchange_snapshot_pair
SET currency_one_item_id = @CanonicalItemId
WHERE currency_one_item_id = @RetiredItemId;

UPDATE currency_exchange_snapshot_pair
SET currency_two_item_id = @CanonicalItemId
WHERE currency_two_item_id = @RetiredItemId;

UPDATE currency_exchange_history
SET currency_one_item_id = @CanonicalItemId
WHERE currency_one_item_id = @RetiredItemId;

UPDATE currency_exchange_history
SET currency_two_item_id = @CanonicalItemId
WHERE currency_two_item_id = @RetiredItemId;

UPDATE league
SET base_currency_item_id = @CanonicalItemId
WHERE base_currency_item_id = @RetiredItemId;

DELETE FROM game_currency_bridge retired
USING game_currency_bridge canonical
WHERE retired.currency_item_id = @RetiredCurrencyItemId
  AND canonical.currency_item_id = @CanonicalCurrencyItemId
  AND retired.game_id = canonical.game_id;

UPDATE game_currency_bridge
SET currency_item_id = @CanonicalCurrencyItemId
WHERE currency_item_id = @RetiredCurrencyItemId;

INSERT INTO item_daily_stats (
    realm_id,
    item_id,
    league_id,
    day,
    open_price,
    close_price,
    min_price,
    max_price,
    avg_price,
    data_points,
    volume
)
SELECT
    realm_id,
    @CanonicalItemId,
    league_id,
    created_at::date,
    (ARRAY_AGG(price ORDER BY created_at, price_log_id))[1],
    (ARRAY_AGG(price ORDER BY created_at DESC, price_log_id DESC))[1],
    MIN(price),
    MAX(price),
    AVG(price),
    COUNT(*)::int,
    SUM(quantity)::int
FROM price_log
WHERE item_id = @CanonicalItemId
GROUP BY realm_id, league_id, created_at::date;

DELETE FROM currency_item
WHERE currency_item_id = @RetiredCurrencyItemId;

DELETE FROM item
WHERE item_id = @RetiredItemId
  AND NOT EXISTS (
    SELECT 1 FROM currency_item WHERE item_id = @RetiredItemId
  )
  AND NOT EXISTS (
    SELECT 1 FROM unique_item WHERE item_id = @RetiredItemId
  );

DELETE FROM base_item
WHERE base_item_id = @RetiredBaseItemId
  AND NOT EXISTS (
    SELECT 1 FROM item WHERE base_item_id = @RetiredBaseItemId
  );

DELETE FROM item_type
WHERE item_type_id = @RetiredItemTypeId
  AND NOT EXISTS (
    SELECT 1 FROM base_item WHERE item_type_id = @RetiredItemTypeId
  );
""";
    await connection.ExecuteAsync(
      mergeSql,
      ids,
      transaction,
      commandTimeout: commandTimeout);
  }

  private sealed record AliasRow(
    int CurrencyItemId,
    int ItemId,
    int BaseItemId,
    int ItemTypeId,
    string ApiId);
}
