namespace Poe2scout.Repositories.PriceLog.Models;

public record ItemHistoryLog(
  decimal Price,
  DateTime Time,
  int Quantity);
