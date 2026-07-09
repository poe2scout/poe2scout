namespace Poe2scout.Repositories.PriceLog.Models;

public record DailyStatsHistoryEntry(
  DateOnly Day,
  double OpenPrice,
  double ClosePrice,
  double MinPrice,
  double MaxPrice,
  double AvgPrice,
  int Volume);
