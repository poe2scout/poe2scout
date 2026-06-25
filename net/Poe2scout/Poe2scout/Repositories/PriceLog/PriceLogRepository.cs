using Dapper;
using System.Data.Common;
using Poe2scout.Models;
using Poe2scout.Repositories.PriceLog.Models;

namespace Poe2scout.Repositories.PriceLog;

public class PriceLogRepository(DbDataSource dbDataSource) : BaseRepository(dbDataSource), IPriceLogRepository
{
  public async Task<IReadOnlyList<ItemHistory>> GetAllItemHistories(int leagueId, int realmId)
    => await WithConnection(async connection =>
    {
      const string query = """
WITH RECURSIVE distinct_items AS (
    (SELECT item_id
       FROM price_log
      WHERE league_id = @LeagueId
        AND realm_id = @RealmId
      ORDER BY item_id
      LIMIT 1)

     UNION ALL

    SELECT (
        SELECT item_id
          FROM price_log
         WHERE league_id = @LeagueId 
           AND item_id > di.item_id
           AND realm_id = @RealmId
         ORDER BY item_id
         LIMIT 1
    )
      FROM distinct_items di
     WHERE di.item_id IS NOT NULL
)
SELECT p.item_id AS "item_id",
       p.created_at AS "time",
       p.price AS "price",
       p.quantity AS "quantity"
FROM (
    SELECT item_id FROM distinct_items WHERE item_id IS NOT NULL
) AS items
CROSS JOIN LATERAL (
    SELECT created_at, price, quantity, item_id
      FROM price_log
     WHERE league_id = @LeagueId 
       AND realm_id = @RealmId
       AND price_log.item_id = items.item_id
     ORDER BY created_at DESC
     LIMIT 24
) AS p
ORDER BY p.item_id, p.created_at DESC;
""";

      var rows = (await connection.QueryAsync<AllItemHistoriesRow>(
        query,
        new { LeagueId = leagueId, RealmId = realmId })).AsList();

      if (rows.Count == 0)
      {
        return [];
      }

      return rows
        .GroupBy(row => row.ItemId)
        .Select(group => new ItemHistory(
          group.Key,
          group.Select(row => new ItemHistoryLog(
            decimal.Round(row.Price, 3, MidpointRounding.AwayFromZero),
            row.Time,
            row.Quantity)).ToList()))
        .ToList();
    });

  public async Task<IReadOnlyList<ItemDailyStats>> GetItemDailyStats(
    IReadOnlyList<int> itemIds,
    int leagueId,
    int realmId,
    IReadOnlyList<DateOnly> dates)
    => await WithConnection(async connection =>
    {
      if (itemIds.Count == 0 || dates.Count == 0)
      {
        return [];
      }

      const string query = """
            SELECT ids.item_id
                 , ids.avg_price
                 , ids.data_points
                 , ids.volume
                 , ids.day
              FROM item_daily_stats ids
             WHERE ids.day = ANY(@Dates::date[])
               AND ids.item_id = ANY(@ItemIds::int[])
               AND ids.realm_id = @RealmId
               AND ids.league_id = @LeagueId
""";

      return (await connection.QueryAsync<ItemDailyStats>(
        query,
        new
        {
          Dates = dates.ToArray(),
          ItemIds = itemIds.ToArray(),
          LeagueId = leagueId,
          RealmId = realmId
        })).AsList();
    });

  public async Task<IReadOnlyList<DailyStatsHistoryEntry>> GetItemDailyStatsHistory(
    int itemId,
    int leagueId,
    int realmId,
    int limit,
    DateOnly? endDate)
    => await WithConnection(async connection =>
    {
      const string query = """
SELECT
    day,
    open_price,
    close_price,
    min_price,
    max_price,
    avg_price,
    volume
FROM item_daily_stats
WHERE item_id = @ItemId
AND league_id = @LeagueId
AND realm_id = @RealmId
AND (@EndDate::date IS NULL OR day < @EndDate::date)
ORDER BY day DESC
LIMIT @Limit;
""";

      return (await connection.QueryAsync<DailyStatsHistoryEntry>(
        query,
        new { ItemId = itemId, LeagueId = leagueId, RealmId = realmId, EndDate = endDate, Limit = limit })).AsList();
    });

  public async Task<Dictionary<int, IReadOnlyList<PriceLogEntry?>>> GetItemPriceBucketStats(
    IReadOnlyList<int> itemIds,
    int leagueId,
    int realmId,
    IReadOnlyList<DateTime> bucketStarts,
    int frequencyHours)
    => await WithConnection(async connection =>
    {
      if (itemIds.Count == 0 || bucketStarts.Count == 0)
      {
        return [];
      }

      const string query = """
            WITH time_blocks AS (
                SELECT
                    block_start,
                    block_start + (@FrequencyHours * interval '1 hour') AS block_end,
                    block_index
                FROM unnest(
                    @BlockStarts::timestamp[],
                    @BlockIndices::int[]
                ) AS tb(block_start, block_index)
            ),
            item_blocks AS (
                SELECT
                    item_id,
                    tb.block_start,
                    tb.block_end,
                    tb.block_index
                FROM unnest(@ItemIds::int[]) AS req(item_id)
                CROSS JOIN time_blocks tb
            )
            SELECT
                ib.item_id AS "item_id",
                ib.block_index AS "block_index",
                bucket.price AS "price",
                bucket.quantity AS "quantity",
                ib.block_start AS "time"
            FROM item_blocks ib
            LEFT JOIN LATERAL (
                SELECT
                    avg(pl.price)::double precision AS price,
                    sum(pl.quantity)::int AS quantity
                FROM price_log pl
                WHERE pl.item_id = ib.item_id
                  AND pl.league_id = @LeagueId
                  AND pl.realm_id = @RealmId
                  AND pl.created_at >= ib.block_start
                  AND pl.created_at < ib.block_end
            ) AS bucket ON TRUE
            ORDER BY ib.item_id, ib.block_index;
""";

      var rows = await connection.QueryAsync<BucketStatsRow>(
        query,
        new
        {
          BlockStarts = bucketStarts.ToArray(),
          BlockIndices = Enumerable.Range(0, bucketStarts.Count).ToArray(),
          ItemIds = itemIds.ToArray(),
          LeagueId = leagueId,
          RealmId = realmId,
          FrequencyHours = frequencyHours
        });

      var results = itemIds.ToDictionary(
        itemId => itemId,
        _ => (IReadOnlyList<PriceLogEntry?>)Enumerable.Repeat<PriceLogEntry?>(null, bucketStarts.Count).ToList());

      foreach (var row in rows)
      {
        if (row.Price is null || row.Quantity is null)
        {
          continue;
        }

        ((List<PriceLogEntry?>)results[row.ItemId])[row.BlockIndex] = new PriceLogEntry(
          row.Price.Value,
          row.Time,
          row.Quantity.Value);
      }

      return results;
    });

  public async Task<double> GetItemPrice(int itemId, int leagueId, int realmId, int? epoch)
    => await WithConnection(async connection =>
    {
      epoch ??= (int)DateTimeOffset.UtcNow.ToUnixTimeSeconds();
      var createdBefore = DateTimeOffset.FromUnixTimeSeconds(epoch.Value).LocalDateTime;

      const string query = """
            SELECT price FROM price_log
            WHERE item_id = @ItemId
              AND league_id = @LeagueId
              AND realm_id = @RealmId
              AND created_at < @CreatedBefore
            ORDER BY created_at DESC
            LIMIT 1
""";

      var price = await connection.QuerySingleOrDefaultAsync<double?>(
        query,
        new { ItemId = itemId, LeagueId = leagueId, RealmId = realmId, CreatedBefore = createdBefore });

      return price ?? 0;
    });

  public async Task<ItemPriceHistory> GetItemPriceHistory(
    int itemId,
    int leagueId,
    int realmId,
    int logCount,
    int logFrequency,
    DateTime endTime)
    => await WithConnection(async connection =>
    {
      var limit = logCount + 1;

      const string query = """
SELECT DISTINCT ON (time)
    price,
    quantity,
    date_bin(
        (@LogFrequency || ' hours')::interval,
        created_at,
        @EndTime::timestamp
    ) AS time
FROM price_log
WHERE item_id = @ItemId
AND league_id = @LeagueId
AND realm_id = @RealmId
AND created_at < @EndTime
ORDER BY time DESC, created_at DESC
LIMIT @Limit;
""";

      var priceLogs = (await connection.QueryAsync<PriceLogEntry>(
        query,
        new
        {
          LogFrequency = logFrequency,
          EndTime = endTime,
          ItemId = itemId,
          RealmId = realmId,
          LeagueId = leagueId,
          Limit = limit
        })).AsList();

      var hasMore = priceLogs.Count > logCount;
      if (hasMore)
      {
        priceLogs = priceLogs.Take(logCount).ToList();
      }

      return new ItemPriceHistory(priceLogs, hasMore);
    });

  public async Task<Dictionary<int, IReadOnlyList<PriceLogEntry?>>> GetItemPriceLogs(
    IReadOnlyList<int> itemIds,
    int leagueId,
    int realmId)
    => await WithConnection(async connection =>
    {
      var now = DateTime.Now;
      var currentBlock = new DateTime(now.Year, now.Month, now.Day, (now.Hour / 6) * 6, 0, 0, now.Kind);
      var timeBlocks = Enumerable.Range(0, 7).Select(index => currentBlock.AddHours(index * -6)).ToArray();

      const string query = """
            WITH time_blocks AS (
                SELECT
                    block_start,
                    block_start + interval '6 hours' as block_end,
                    block_index
                FROM unnest(
                    @BlockTimestamps::timestamp[], 
                    @BlockIndices::int[]) AS tb(block_start, 
                    block_index)
            ),
            item_blocks AS (
                SELECT
                    i.item_id,
                    tb.block_start,
                    tb.block_end,
                    tb.block_index
                FROM time_blocks tb
                CROSS JOIN unnest(@ItemIds::int[]) AS i(item_id)
            ),
            latest_prices AS (
                SELECT
                    ib.item_id,
                    ib.block_start,
                    ib.block_index,
                    pl."price",
                    ROW_NUMBER() OVER (
                        PARTITION BY ib.item_id, ib.block_start
                        ORDER BY pl.created_at DESC
                    ) as rn,
                    pl."quantity"
                FROM item_blocks ib
                LEFT JOIN price_log pl ON
                    pl.item_id = ib.item_id
                    AND pl.league_id = @LeagueId
                    AND pl.realm_id = @RealmId
                    AND pl.created_at >= ib.block_start
                    AND pl.created_at < ib.block_end
            )
            SELECT
                item_id as "item_id",
                block_index as "block_index",
                price,
                quantity,
                block_start as "time"
            FROM latest_prices
            WHERE rn = 1
            ORDER BY item_id, block_index;
""";

      var rows = await connection.QueryAsync<BucketStatsRow>(
        query,
        new
        {
          BlockTimestamps = timeBlocks,
          BlockIndices = Enumerable.Range(0, 7).ToArray(),
          ItemIds = itemIds.ToArray(),
          LeagueId = leagueId,
          RealmId = realmId
        });

      var results = itemIds.ToDictionary(
        itemId => itemId,
        _ => (IReadOnlyList<PriceLogEntry?>)Enumerable.Repeat<PriceLogEntry?>(null, 7).ToList());

      foreach (var row in rows)
      {
        if (row.Price is not null && row.Quantity is not null)
        {
          ((List<PriceLogEntry?>)results[row.ItemId])[row.BlockIndex] = new PriceLogEntry(
            row.Price.Value,
            row.Time,
            row.Quantity.Value);
        }
      }

      return results;
    });

  public async Task<IReadOnlyList<ItemPrice>> GetItemPrices(IReadOnlyList<int> itemIds, int leagueId, int realmId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT
                req_item.item_id AS item_id,
                COALESCE(latest_price.price, 0) AS price,
                COALESCE(latest_price.quantity, 0) AS quantity
              FROM UNNEST(@ItemIds) AS req_item(item_id)
              LEFT JOIN LATERAL (
                  SELECT price, quantity
                    FROM price_log
                   WHERE item_id = req_item.item_id
                     AND league_id = @LeagueId
                     AND realm_id = @RealmId
                   ORDER BY created_at DESC
                   LIMIT 1
              ) AS latest_price ON TRUE;
""";

      return (await connection.QueryAsync<ItemPrice>(
        query,
        new { ItemIds = itemIds.ToArray(), LeagueId = leagueId, RealmId = realmId })).AsList();
    });

  public async Task<IReadOnlyList<ItemPriceByLeague>> GetItemPricesByLeague(
    IReadOnlyList<int> itemIds,
    IReadOnlyList<int> leagueIds,
    int realmId)
    => await WithConnection(async connection =>
    {
      const string query = """
            WITH requested_prices AS (
                SELECT req_league.league_id
                     , req_item.item_id
                  FROM UNNEST(@LeagueIds) AS req_league(league_id)
                 CROSS JOIN UNNEST(@ItemIds) AS req_item(item_id)
            )
            SELECT requested_prices.league_id
                 , requested_prices.item_id
                 , COALESCE(latest_price.price, 0) AS price
              FROM requested_prices
              LEFT JOIN LATERAL (
                  SELECT price
                    FROM price_log
                   WHERE item_id = requested_prices.item_id
                     AND league_id = requested_prices.league_id
                     AND realm_id = @RealmId
                   ORDER BY created_at DESC
                   LIMIT 1
              ) AS latest_price ON TRUE;
""";

      return (await connection.QueryAsync<ItemPriceByLeague>(
        query,
        new { ItemIds = itemIds.ToArray(), LeagueIds = leagueIds.ToArray(), RealmId = realmId })).AsList();
    });

  public async Task<IReadOnlyList<ItemPriceBefore>> GetItemPricesBefore(
    IReadOnlyList<int> itemIds,
    int leagueId,
    int realmId,
    int epoch)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT
                req_item.item_id AS item_id,
                COALESCE(latest_price.price, 0) AS price
              FROM UNNEST(@ItemIds) AS req_item(item_id)
              LEFT JOIN LATERAL (
                  SELECT price
                    FROM price_log
                   WHERE item_id = req_item.item_id
                     AND league_id = @LeagueId
                     AND realm_id = @RealmId
                     AND created_at < to_timestamp(@CreatedAt)
                   ORDER BY created_at DESC
                   LIMIT 1
              ) AS latest_price ON TRUE;
""";

      return (await connection.QueryAsync<ItemPriceBefore>(
        query,
        new { ItemIds = itemIds.ToArray(), LeagueId = leagueId, RealmId = realmId, CreatedAt = epoch })).AsList();
    });

  public async Task<IReadOnlyList<ItemPriceInRange>> GetItemPricesInRange(
    IReadOnlyList<int> itemIds,
    int leagueId,
    int realmId,
    DateTime startTime,
    DateTime endTime)
    => await WithConnection(async connection =>
    {
      const string query = """
            WITH first_price AS (
                SELECT DISTINCT ON (item_id)
                       item_id,
                       price,
                       quantity
                  FROM price_log
                 WHERE league_id = @LeagueId
                   AND realm_id = @RealmId
                   AND created_at >= @StartTime
                   AND created_at < @EndTime
                   AND item_id = ANY(@ItemIds)
                 ORDER BY item_id, created_at ASC
            )
            SELECT
                req_item.item_id AS item_id,
                COALESCE(fp.price, 0) AS price,
                COALESCE(fp.quantity, 0) AS quantity
              FROM UNNEST(@ItemIds) AS req_item(item_id)
              LEFT JOIN first_price AS fp ON req_item.item_id = fp.item_id;
""";

      return (await connection.QueryAsync<ItemPriceInRange>(
        query,
        new
        {
          ItemIds = itemIds.ToArray(),
          LeagueId = leagueId,
          RealmId = realmId,
          StartTime = startTime,
          EndTime = endTime
        })).AsList();
    });

  public async Task<bool> GetPricesChecked(int epoch, int leagueId, int realmId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT
                CASE
                    WHEN EXISTS(
                        SELECT 1 FROM price_log
                        WHERE created_at = to_timestamp(@Epoch)
                        AND league_id = @LeagueId
                        AND realm_id = @RealmId
                    )
                    THEN 1
                    ELSE 0
                END;
""";

      return Convert.ToBoolean(await connection.QuerySingleAsync<int>(
        query,
        new { Epoch = epoch, LeagueId = leagueId, RealmId = realmId }));
    });

  public async Task RecordPrice(RecordPriceModel price)
    => await WithConnection(async connection =>
    {
      const string query = """
WITH inserted_price_log AS (
    INSERT INTO price_log (item_id, league_id, realm_id, price, quantity, created_at)
    VALUES (@ItemId, @LeagueId, @RealmId, @Price, @Quantity, NOW())
    RETURNING item_id, league_id, realm_id, price, quantity, created_at
),
inserted_daily_stats AS (
    SELECT
        realm_id,
        item_id,
        league_id,
        created_at,
        price AS open_price,
        price AS close_price,
        price AS min_price,
        price AS max_price,
        price AS avg_price,
        1 AS data_points,
        quantity AS volume
    FROM inserted_price_log
)
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
    inserted.realm_id,
    inserted.item_id,
    inserted.league_id,
    inserted.created_at::date AS day,
    inserted.open_price,
    inserted.close_price,
    inserted.min_price,
    inserted.max_price,
    inserted.avg_price,
    inserted.data_points,
    inserted.volume
FROM inserted_daily_stats AS inserted
ON CONFLICT (realm_id, item_id, league_id, day) DO UPDATE SET
    close_price = EXCLUDED.close_price,
    min_price = LEAST(item_daily_stats.min_price, EXCLUDED.min_price),
    max_price = GREATEST(item_daily_stats.max_price, EXCLUDED.max_price),
    avg_price = (
        (item_daily_stats.avg_price * item_daily_stats.data_points)
        + (EXCLUDED.avg_price * EXCLUDED.data_points)
    ) / (item_daily_stats.data_points + EXCLUDED.data_points),
    data_points = item_daily_stats.data_points + EXCLUDED.data_points,
    volume = item_daily_stats.volume + EXCLUDED.volume
""";

      await connection.ExecuteAsync(query, price);
      return true;
    });

  public async Task RecordPriceBulk(IReadOnlyList<RecordPriceModel> prices, int epoch)
    => await WithConnection(async connection =>
    {
      if (prices.Count == 0)
      {
        throw new ArgumentException("record_price_bulk requires at least one price", nameof(prices));
      }

      var seenPriceKeys = new HashSet<(int RealmId, int ItemId, int LeagueId)>();
      foreach (var price in prices)
      {
        var priceKey = (price.RealmId, price.ItemId, price.LeagueId);
        if (!seenPriceKeys.Add(priceKey))
        {
          throw new ArgumentException(
            "record_price_bulk received multiple prices for the same realm_id, item_id, and league_id",
            nameof(prices));
        }
      }

      const string query = """
WITH input_prices AS (
    SELECT
        item_id,
        league_id,
        realm_id,
        price,
        quantity,
        to_timestamp(@CreatedAt)::timestamp AS created_at
    FROM unnest(
        @ItemIds::int[],
        @LeagueIds::int[],
        @RealmIds::int[],
        @Prices::double precision[],
        @Quantities::int[]
    ) AS price_input(
        item_id,
        league_id,
        realm_id,
        price,
        quantity
    )
),
inserted_price_log AS (
    INSERT INTO price_log (item_id, league_id, realm_id, price, quantity, created_at)
    SELECT item_id, league_id, realm_id, price, quantity, created_at
    FROM input_prices
    RETURNING item_id, league_id, realm_id, price, quantity, created_at
),
inserted_daily_stats AS (
    SELECT
        realm_id,
        item_id,
        league_id,
        created_at,
        price AS open_price,
        price AS close_price,
        price AS min_price,
        price AS max_price,
        price AS avg_price,
        1 AS data_points,
        quantity AS volume
    FROM inserted_price_log
)
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
    inserted.realm_id,
    inserted.item_id,
    inserted.league_id,
    inserted.created_at::date AS day,
    inserted.open_price,
    inserted.close_price,
    inserted.min_price,
    inserted.max_price,
    inserted.avg_price,
    inserted.data_points,
    inserted.volume
FROM inserted_daily_stats AS inserted
ON CONFLICT (realm_id, item_id, league_id, day) DO UPDATE SET
    close_price = EXCLUDED.close_price,
    min_price = LEAST(item_daily_stats.min_price, EXCLUDED.min_price),
    max_price = GREATEST(item_daily_stats.max_price, EXCLUDED.max_price),
    avg_price = (
        (item_daily_stats.avg_price * item_daily_stats.data_points)
        + (EXCLUDED.avg_price * EXCLUDED.data_points)
    ) / (item_daily_stats.data_points + EXCLUDED.data_points),
    data_points = item_daily_stats.data_points + EXCLUDED.data_points,
    volume = item_daily_stats.volume + EXCLUDED.volume
""";

      await connection.ExecuteAsync(
        query,
        new
        {
          ItemIds = prices.Select(price => price.ItemId).ToArray(),
          LeagueIds = prices.Select(price => price.LeagueId).ToArray(),
          RealmIds = prices.Select(price => price.RealmId).ToArray(),
          Prices = prices.Select(price => price.Price).ToArray(),
          Quantities = prices.Select(price => price.Quantity).ToArray(),
          CreatedAt = epoch
        });
      return true;
    });

  private sealed record AllItemHistoriesRow(int ItemId, DateTime Time, decimal Price, int Quantity);

  private sealed record BucketStatsRow(
    int ItemId,
    int BlockIndex,
    double? Price,
    int? Quantity,
    DateTime Time);
}
