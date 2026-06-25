using Dapper;
using System.Data.Common;
using Poe2scout.Repositories.CurrencyExchange.Models;

namespace Poe2scout.Repositories.CurrencyExchange;

public class CurrencyExchangeRepository(DbDataSource dbDataSource)
  : BaseRepository(dbDataSource), ICurrencyExchangeRepository
{
  public async Task<int?> CreateSnapshot(CurrencyExchangeSnapshot snapshot)
    => await WithConnection(async connection =>
    {
      if (snapshot.Pairs.Count == 0)
      {
        const string emptySnapshotQuery = """
INSERT INTO currency_exchange_snapshot(epoch, league_id, realm_id, volume, market_cap)
VALUES(@Epoch, @LeagueId, @RealmId, @Volume, @MarketCap)
RETURNING currency_exchange_snapshot_id
""";

        return await connection.QuerySingleOrDefaultAsync<int?>(
          emptySnapshotQuery,
          new
          {
            snapshot.Epoch,
            snapshot.LeagueId,
            snapshot.RealmId,
            snapshot.Volume,
            snapshot.MarketCap
          });
      }

      const string query = """
WITH snapshot_insert AS (
    INSERT INTO currency_exchange_snapshot(epoch, league_id, realm_id, volume, market_cap)
    VALUES (@Epoch, @LeagueId, @RealmId, @Volume, @MarketCap)
    RETURNING currency_exchange_snapshot_id
),
pair_data_unnested AS (
    SELECT
        row_number() OVER () as rn,
        c1_id, c2_id, volume,
        c1_val_traded, c1_vol_traded, c1_stock, c1_price, c1_stock_value,
        c2_val_traded, c2_vol_traded, c2_stock, c2_price, c2_stock_value
    FROM unnest(
        @C1Ids::integer[],
        @C2Ids::integer[],
        @Volumes::decimal[],
        @C1ValTraded::decimal[],
        @C1VolTraded::bigint[],
        @C1Stock::bigint[],
        @C1Price::decimal[],
        @C1StockValue::decimal[],
        @C2ValTraded::decimal[],
        @C2VolTraded::bigint[],
        @C2Stock::bigint[],
        @C2Price::decimal[],
        @C2StockValue::decimal[]
    ) AS t(
        c1_id, c2_id, volume,
        c1_val_traded, c1_vol_traded, c1_stock, c1_price, c1_stock_value,
        c2_val_traded, c2_vol_traded, c2_stock, c2_price, c2_stock_value
    )
),
pair_insert AS (
    INSERT INTO currency_exchange_snapshot_pair (
        currency_exchange_snapshot_id, currency_one_item_id, currency_two_item_id, volume
    )
    SELECT
        (SELECT currency_exchange_snapshot_id FROM snapshot_insert),
        pdu.c1_id,
        pdu.c2_id,
        pdu.volume
    FROM pair_data_unnested AS pdu
    RETURNING currency_exchange_snapshot_pair_id, currency_one_item_id, currency_two_item_id
),
pair_data_to_insert AS (
    SELECT
        pi.currency_exchange_snapshot_pair_id,
        pdu.c1_id AS item_id,
        pdu.c1_val_traded AS value_traded,
        pdu.c1_price AS relative_price,
        pdu.c1_vol_traded AS volume_traded,
        pdu.c1_stock AS highest_stock,
        pdu.c1_stock_value AS stock_value
    FROM pair_insert AS pi
    JOIN pair_data_unnested AS pdu ON pi.currency_one_item_id = pdu.c1_id
                                  AND pi.currency_two_item_id = pdu.c2_id
    UNION ALL
    SELECT
        pi.currency_exchange_snapshot_pair_id,
        pdu.c2_id,
        pdu.c2_val_traded,
        pdu.c2_price,
        pdu.c2_vol_traded,
        pdu.c2_stock,
        pdu.c2_stock_value
    FROM pair_insert AS pi
    JOIN pair_data_unnested AS pdu ON pi.currency_one_item_id = pdu.c1_id
                                  AND pi.currency_two_item_id = pdu.c2_id
),
final_insert AS (
    INSERT INTO currency_exchange_snapshot_pair_data (
        currency_exchange_snapshot_pair_id, item_id, value_traded,
        relative_price, volume_traded, highest_stock, stock_value
    )
    SELECT * FROM pair_data_to_insert
    RETURNING 1
)
SELECT currency_exchange_snapshot_id FROM snapshot_insert;
""";

      return await connection.QuerySingleAsync<int>(
        query,
        new
        {
          snapshot.Epoch,
          snapshot.LeagueId,
          snapshot.RealmId,
          snapshot.Volume,
          snapshot.MarketCap,
          C1Ids = snapshot.Pairs.Select(pair => pair.CurrencyOneItemId).ToArray(),
          C2Ids = snapshot.Pairs.Select(pair => pair.CurrencyTwoItemId).ToArray(),
          Volumes = snapshot.Pairs.Select(pair => pair.Volume).ToArray(),
          C1ValTraded = snapshot.Pairs.Select(pair => pair.CurrencyOneData.ValueTraded).ToArray(),
          C1VolTraded = snapshot.Pairs.Select(pair => pair.CurrencyOneData.VolumeTraded).ToArray(),
          C1Stock = snapshot.Pairs.Select(pair => pair.CurrencyOneData.HighestStock).ToArray(),
          C1Price = snapshot.Pairs.Select(pair => pair.CurrencyOneData.RelativePrice).ToArray(),
          C1StockValue = snapshot.Pairs.Select(pair => pair.CurrencyOneData.StockValue).ToArray(),
          C2ValTraded = snapshot.Pairs.Select(pair => pair.CurrencyTwoData.ValueTraded).ToArray(),
          C2VolTraded = snapshot.Pairs.Select(pair => pair.CurrencyTwoData.VolumeTraded).ToArray(),
          C2Stock = snapshot.Pairs.Select(pair => pair.CurrencyTwoData.HighestStock).ToArray(),
          C2Price = snapshot.Pairs.Select(pair => pair.CurrencyTwoData.RelativePrice).ToArray(),
          C2StockValue = snapshot.Pairs.Select(pair => pair.CurrencyTwoData.StockValue).ToArray()
        });
    });

  public async Task<CurrencyExchangeHistory> GetCurrencyExchangeHistory(
    int leagueId,
    int realmId,
    int endTime,
    int limit)
    => await WithConnection(async connection =>
    {
      const string query = """
                SELECT epoch,
                       market_cap,
                       volume
                  FROM currency_exchange_snapshot
                 WHERE league_id = @LeagueId
                   AND realm_id = @RealmId
                   AND epoch < @EndTime
                 ORDER BY
                       epoch DESC
                 LIMIT @Limit
""";

      var records = (await connection.QueryAsync<CurrencyExchangeHistoryEntry>(
        query,
        new { LeagueId = leagueId, RealmId = realmId, EndTime = endTime, Limit = limit + 1 })).AsList();

      var hasMore = false;
      if (records.Count > limit)
      {
        hasMore = true;
        records.RemoveAt(records.Count - 1);
      }

      return new CurrencyExchangeHistory(
        new Dictionary<string, bool> { ["has_more"] = hasMore },
        records);
    });

  public async Task<IReadOnlyList<SnapshotPair>> GetCurrentSnapshotPairs(int leagueId, int realmId)
    => await WithConnection(async connection =>
    {
      const string query = """
WITH current_snapshot_id AS (
  SELECT currency_exchange_snapshot_id
    FROM currency_exchange_snapshot
   WHERE league_id = @LeagueId
     AND realm_id = @RealmId
   ORDER BY epoch DESC
   LIMIT 1
)
SELECT cesp.currency_exchange_snapshot_pair_id AS currency_exchange_snapshot_pair_id,
       cesp.currency_exchange_snapshot_id AS currency_exchange_snapshot_id,
       cesp.volume AS volume,
       ci1.currency_item_id AS c1_currency_item_id,
       ci1.item_id AS c1_item_id,
       ci1.api_id AS c1_api_id,
       ci1.text AS c1_text,
       ci1.icon_url AS c1_icon_url,
       ci1.item_category_id AS c1_currency_category_id,
       cc1.label AS c1_cat_label,
       cc1.api_id AS c1_cat_api_id,
       ci2.currency_item_id AS c2_currency_item_id,
       ci2.item_id AS c2_item_id,
       ci2.api_id AS c2_api_id,
       ci2.text AS c2_text,
       ci2.icon_url AS c2_icon_url,
       ci2.item_category_id AS c2_currency_category_id,
       cc2.label AS c2_cat_label,
       cc2.api_id AS c2_cat_api_id,
       cespd1.value_traded AS c1_value_traded,
       cespd1.relative_price AS c1_relative_price,
       cespd1.stock_value AS c1_stock_value,
       cespd1.volume_traded AS c1_volume_traded,
       cespd1.highest_stock AS c1_highest_stock,
       cespd2.value_traded AS c2_value_traded,
       cespd2.relative_price AS c2_relative_price,
       cespd2.stock_value AS c2_stock_value,
       cespd2.volume_traded AS c2_volume_traded,
       cespd2.highest_stock AS c2_highest_stock
  FROM currency_exchange_snapshot_pair AS cesp
  JOIN currency_item AS ci1 ON cesp.currency_one_item_id = ci1.item_id
  JOIN item_category AS cc1 ON ci1.item_category_id = cc1.item_category_id
  JOIN currency_item AS ci2 ON cesp.currency_two_item_id = ci2.item_id
  JOIN item_category AS cc2 ON ci2.item_category_id = cc2.item_category_id
  JOIN currency_exchange_snapshot_pair_data AS cespd1
        ON cespd1.currency_exchange_snapshot_pair_id = cesp.currency_exchange_snapshot_pair_id
        AND cespd1.item_id = cesp.currency_one_item_id
  JOIN currency_exchange_snapshot_pair_data AS cespd2
        ON cespd2.currency_exchange_snapshot_pair_id = cesp.currency_exchange_snapshot_pair_id
        AND cespd2.item_id = cesp.currency_two_item_id
 WHERE cesp.currency_exchange_snapshot_id IN (SELECT currency_exchange_snapshot_id
                                               FROM current_snapshot_id);
""";

      var rows = await connection.QueryAsync<FlatSnapshotPairRow>(
        query,
        new { LeagueId = leagueId, RealmId = realmId });

      return rows.Select(row =>
      {
        var currencyOne = new Poe2scout.Models.CurrencyItem(
          row.C1CurrencyItemId,
          row.C1ItemId,
          row.C1CurrencyCategoryId,
          row.C1ApiId,
          row.C1Text,
          row.C1CatApiId,
          row.C1IconUrl,
          null);

        var currencyTwo = new Poe2scout.Models.CurrencyItem(
          row.C2CurrencyItemId,
          row.C2ItemId,
          row.C2CurrencyCategoryId,
          row.C2ApiId,
          row.C2Text,
          row.C2CatApiId,
          row.C2IconUrl,
          null);

        return new SnapshotPair(
          row.CurrencyExchangeSnapshotPairId,
          row.CurrencyExchangeSnapshotId,
          row.Volume,
          currencyOne,
          currencyTwo,
          new PairData(
            row.C1ValueTraded,
            row.C1RelativePrice,
            row.C1StockValue,
            row.C1VolumeTraded,
            row.C1HighestStock),
          new PairData(
            row.C2ValueTraded,
            row.C2RelativePrice,
            row.C2StockValue,
            row.C2VolumeTraded,
            row.C2HighestStock));
      }).ToList();
    });

  public async Task<CurrencyExchangeData?> GetCurrencyExchange(int leagueId, int realmId)
    => await WithConnection(connection =>
    {
      const string query = """
            SELECT epoch,
                   volume,
                   market_cap
              FROM currency_exchange_snapshot
             WHERE league_id = @LeagueId
               AND realm_id = @RealmId
             ORDER BY epoch DESC
             LIMIT 1
""";

      return connection.QuerySingleOrDefaultAsync<CurrencyExchangeData>(
        query,
        new { LeagueId = leagueId, RealmId = realmId });
    });

  public async Task<IReadOnlyList<int>> GetExistingSnapshotLeagueIds(int epoch, int realmId)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT league_id
              FROM currency_exchange_snapshot
             WHERE epoch = @Epoch
               AND realm_id = @RealmId
""";

      return (await connection.QueryAsync<int>(query, new { Epoch = epoch, RealmId = realmId })).AsList();
    });

  public async Task<PairHistory> GetPairHistory(
    int leagueId,
    int realmId,
    int currencyOneId,
    int currencyTwoId,
    int endEpoch,
    int limit)
    => await WithConnection(async connection =>
    {
      const string query = """
(
    SELECT
        epoch,
        currency_one_item_id AS "currency_one_id",
        c1_value_traded AS "c1_value_traded",
        c1_relative_price AS "c1_relative_price",
        c1_stock_value AS "c1_stock_value",
        c1_volume_traded AS "c1_volume_traded",
        c1_highest_stock AS "c1_highest_stock",
        currency_two_item_id AS "currency_two_id",
        c2_value_traded AS "c2_value_traded",
        c2_relative_price AS "c2_relative_price",
        c2_stock_value AS "c2_stock_value",
        c2_volume_traded AS "c2_volume_traded",
        c2_highest_stock AS "c2_highest_stock"
    FROM currency_exchange_history
    WHERE
        league_id = @LeagueId
        AND realm_id = @RealmId
        AND epoch < @EndEpoch
        AND currency_one_item_id = @CurrencyTwoId
        AND currency_two_item_id = @CurrencyOneId
    ORDER BY epoch DESC
    LIMIT @Limit
)
UNION ALL
(
    SELECT
        epoch AS "epoch",
        currency_one_item_id AS "currency_one_id",
        c1_value_traded AS "c1_value_traded",
        c1_relative_price AS "c1_relative_price",
        c1_stock_value AS "c1_stock_value",
        c1_volume_traded AS "c1_volume_traded",
        c1_highest_stock AS "c1_highest_stock",
        currency_two_item_id AS "currency_two_id",
        c2_value_traded AS "c2_value_traded",
        c2_relative_price AS "c2_relative_price",
        c2_stock_value AS "c2_stock_value",
        c2_volume_traded AS "c2_volume_traded",
        c2_highest_stock AS "c2_highest_stock"
    FROM currency_exchange_history
    WHERE
        league_id = @LeagueId
        AND realm_id = @RealmId
        AND epoch < @EndEpoch
        AND currency_one_item_id = @CurrencyOneId
        AND currency_two_item_id = @CurrencyTwoId
    ORDER BY epoch DESC
    LIMIT @Limit
)
ORDER BY "epoch" DESC
LIMIT @Limit;
""";

      var records = (await connection.QueryAsync<PairHistoryDbRow>(
        query,
        new
        {
          CurrencyOneId = currencyOneId,
          CurrencyTwoId = currencyTwoId,
          LeagueId = leagueId,
          RealmId = realmId,
          EndEpoch = endEpoch,
          Limit = limit + 1
        })).AsList();

      var hasMore = false;
      if (records.Count > limit)
      {
        hasMore = true;
        records.RemoveAt(records.Count - 1);
      }

      var history = new List<PairHistoryEntry>();
      foreach (var record in records)
      {
        var currencyOneData = new PairHistoryEntryDataDetails(
          record.CurrencyOneId,
          record.C1ValueTraded,
          record.C1RelativePrice,
          record.C1StockValue,
          record.C1VolumeTraded,
          record.C1HighestStock);

        var currencyTwoData = new PairHistoryEntryDataDetails(
          record.CurrencyTwoId,
          record.C2ValueTraded,
          record.C2RelativePrice,
          record.C2StockValue,
          record.C2VolumeTraded,
          record.C2HighestStock);

        var data = currencyOneData.CurrencyItemId == currencyOneId
          ? new PairHistoryEntryData(currencyOneData, currencyTwoData)
          : new PairHistoryEntryData(currencyTwoData, currencyOneData);

        history.Add(new PairHistoryEntry(record.Epoch, data));
      }

      return new PairHistory(
        history,
        new Dictionary<string, object> { ["has_more"] = hasMore });
    });

  public async Task UpdatePairHistories()
    => await WithConnection(async connection =>
    {
      const string query = """
SELECT update_currency_history_incrementally();
""";

      await connection.ExecuteAsync(query);
      return true;
    });

  private sealed record FlatSnapshotPairRow(
    int CurrencyExchangeSnapshotPairId,
    int CurrencyExchangeSnapshotId,
    double Volume,
    int C1CurrencyItemId,
    int C1ItemId,
    string C1ApiId,
    string C1Text,
    string? C1IconUrl,
    int C1CurrencyCategoryId,
    string C1CatLabel,
    string C1CatApiId,
    int C2CurrencyItemId,
    int C2ItemId,
    string C2ApiId,
    string C2Text,
    string? C2IconUrl,
    int C2CurrencyCategoryId,
    string C2CatLabel,
    string C2CatApiId,
    double C1ValueTraded,
    double C2ValueTraded,
    double C1RelativePrice,
    double C2RelativePrice,
    double C1StockValue,
    double C2StockValue,
    int C1VolumeTraded,
    int C2VolumeTraded,
    int C1HighestStock,
    int C2HighestStock);

  private sealed record PairHistoryDbRow(
    int Epoch,
    int CurrencyOneId,
    double C1ValueTraded,
    double C1RelativePrice,
    double C1StockValue,
    int C1VolumeTraded,
    int C1HighestStock,
    int CurrencyTwoId,
    double C2ValueTraded,
    double C2RelativePrice,
    double C2StockValue,
    int C2VolumeTraded,
    int C2HighestStock);
}
