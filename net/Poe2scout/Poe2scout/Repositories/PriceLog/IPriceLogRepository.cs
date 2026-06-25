using Poe2scout.Models;
using Poe2scout.Repositories.PriceLog.Models;

namespace Poe2scout.Repositories.PriceLog;

public interface IPriceLogRepository
{
  public Task<IReadOnlyList<ItemHistory>> GetAllItemHistories(int leagueId, int realmId);
  public Task<IReadOnlyList<ItemDailyStats>> GetItemDailyStats(IReadOnlyList<int> itemIds, int leagueId, int realmId, IReadOnlyList<DateOnly> dates);
  public Task<IReadOnlyList<DailyStatsHistoryEntry>> GetItemDailyStatsHistory(int itemId, int leagueId, int realmId, int limit, DateOnly? endDate);
  public Task<Dictionary<int, IReadOnlyList<PriceLogEntry?>>> GetItemPriceBucketStats(IReadOnlyList<int> itemIds, int leagueId, int realmId, IReadOnlyList<DateTime> bucketStarts, int frequencyHours);
  public Task<double> GetItemPrice(int itemId, int leagueId, int realmId, int? epoch);
  public Task<ItemPriceHistory> GetItemPriceHistory(int itemId, int leagueId, int realmId, int logCount, int logFrequency, DateTime endTime);
  public Task<Dictionary<int, IReadOnlyList<PriceLogEntry?>>> GetItemPriceLogs(IReadOnlyList<int> itemIds, int leagueId, int realmId);
  public Task<IReadOnlyList<ItemPrice>> GetItemPrices(IReadOnlyList<int> itemIds, int leagueId, int realmId);
  public Task<IReadOnlyList<ItemPriceByLeague>> GetItemPricesByLeague(IReadOnlyList<int> itemIds, IReadOnlyList<int> leagueIds, int realmId);
  public Task<IReadOnlyList<ItemPriceBefore>> GetItemPricesBefore(IReadOnlyList<int> itemIds, int leagueId, int realmId, int epoch);
  public Task<IReadOnlyList<ItemPriceInRange>> GetItemPricesInRange(IReadOnlyList<int> itemIds, int leagueId, int realmId, DateTime startTime, DateTime endTime);
  public Task<bool> GetPricesChecked(int epoch, int leagueId, int realmId);
  public Task RecordPrice(RecordPriceModel price);
  public Task RecordPriceBulk(IReadOnlyList<RecordPriceModel> prices, int epoch);
}
