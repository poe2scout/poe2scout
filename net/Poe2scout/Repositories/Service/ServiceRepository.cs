using Dapper;
using System.Data.Common;
using Poe2scout.Repositories.Service.Models;

namespace Poe2scout.Repositories.Service;

public class ServiceRepository(DbDataSource dbDataSource) : BaseRepository(dbDataSource), IServiceRepository
{
  public async Task<bool> GetCurrencyFetchStatus(DateTime startTime)
    => await WithConnection(async connection =>
    {
      const string query = """
            SELECT 1
              FROM currency_item AS ci
              JOIN price_log AS pl ON ci.item_id = pl.item_id
             WHERE pl.created_at >= @StartTime
             LIMIT 1
""";

      return await connection.QueryFirstOrDefaultAsync<int?>(query, new { StartTime = startTime }) is not null;
    });

  public async Task<IReadOnlyList<int>> GetFetchedItemIds(string currentHour, int leagueId)
    => await WithConnection(async connection =>
    {
      var currentHourInt = int.Parse(currentHour);
      var ranges = new[] { new[] { 0, 12 }, new[] { 12, 24 } };

      int? currentStartHour = null;
      int? currentEndHour = null;
      foreach (var hourRange in ranges)
      {
        if (currentHourInt >= hourRange[0] && currentHourInt < hourRange[1])
        {
          currentStartHour = hourRange[0];
          currentEndHour = hourRange[1];
        }
      }

      if (currentStartHour is null || currentEndHour is null)
      {
        throw new InvalidOperationException("Current hour did not match a fetch range");
      }

      var now = DateTime.Now;
      var currentStart = new DateTime(
        now.Year,
        now.Month,
        now.Day,
        currentStartHour.Value,
        0,
        0,
        now.Kind);

      var currentDay = DateTime.Now.Day;
      if (currentEndHour == 24)
      {
        currentEndHour = 0;
        currentDay = DateTime.Now.AddDays(1).Day;
      }

      var currentEnd = new DateTime(
        now.Year,
        now.Month,
        currentDay,
        currentEndHour.Value,
        0,
        0,
        now.Kind);

      const string query = """
            SELECT DISTINCT i.item_id FROM item as i
            JOIN price_log as pl ON i.item_id = pl.item_id
            JOIN league as l ON pl.league_id = l.league_id
            WHERE pl.created_at > @CurrentStart AND pl.created_at < @CurrentEnd AND l.league_id = @LeagueId
""";

      return (await connection.QueryAsync<int>(
        query,
        new { CurrentStart = currentStart, CurrentEnd = currentEnd, LeagueId = leagueId })).AsList();
    });

  public async Task<ServiceCacheValue?> GetServiceCacheValue(string serviceName)
    => await WithConnection(connection =>
    {
      const string query = """
            SELECT value
              FROM service_cache
             WHERE service_name = @ServiceName
""";

      return connection.QuerySingleOrDefaultAsync<ServiceCacheValue>(query, new { ServiceName = serviceName });
    });

  public async Task SetServiceCacheValue(string serviceName, int value)
    => await WithConnection(async connection =>
    {
      const string query = """
            UPDATE service_cache
               SET value = @Value
             WHERE service_name = @ServiceName
""";

      await connection.ExecuteAsync(query, new { ServiceName = serviceName, Value = value });
      return true;
    });
}
