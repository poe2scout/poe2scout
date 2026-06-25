namespace Poe2scout.Repositories.PriceLog.Models;

public record ItemDailyStats(
  int ItemId,
  double AvgPrice,
  int DataPoints,
  int Volume,
  DateOnly Day);
