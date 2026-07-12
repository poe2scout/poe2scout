using Poe2scout.Models;
using Poe2scout.Repositories.PriceLog.Models;

namespace Poe2scout.Repositories.PriceLog;

public interface IPriceLogRepository
{
  public Task<IReadOnlyList<ItemHistory>> GetAllItemHistories(int leagueId, int realmId);
  public Task<IReadOnlyList<ItemDailyStats>> GetItemDailyStats(List<int> itemIds, int leagueId, int realmId, List<DateOnly> dates);
  public Task<IReadOnlyList<DailyStatsHistoryEntry>> GetItemDailyStatsHistory(int itemId, int leagueId, int realmId, int limit, DateOnly? endDate);
  public Task<Dictionary<int, IReadOnlyList<PriceLogEntry?>>> GetItemPriceBucketStats(List<int> itemIds, int leagueId, int realmId, List<DateTime> bucketStarts, int frequencyHours);
  public Task<double> GetItemPrice(int itemId, int leagueId, int realmId, int? epoch);
  public Task<ItemPriceHistory> GetItemPriceHistory(int itemId, int leagueId, int realmId, int logCount, int logFrequency, DateTime endTime);
  public Task<Dictionary<int, IReadOnlyList<PriceLogEntry?>>> GetItemPriceLogs(List<int> itemIds, int leagueId, int realmId);
  public Task<IReadOnlyList<ItemPrice>> GetItemPrices(List<int> itemIds, int leagueId, int realmId);
  public Task<IReadOnlyList<ItemPriceByLeague>> GetItemPricesByLeague(List<int> itemIds, List<int> leagueIds, int realmId);
  public Task<IReadOnlyList<ItemPriceBefore>> GetItemPricesBefore(List<int> itemIds, int leagueId, int realmId, int epoch);
  public Task<IReadOnlyList<ItemPriceInRange>> GetItemPricesInRange(List<int> itemIds, int leagueId, int realmId, DateTime startTime, DateTime endTime);
  public Task<bool> GetPricesChecked(int epoch, int leagueId, int realmId);
  public Task RecordPrice(RecordPriceModel price);
  public Task RecordPriceBulk(List<RecordPriceModel> prices, int epoch);
}
