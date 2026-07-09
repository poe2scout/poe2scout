namespace Poe2scout.Repositories.PriceLog.Models;

public record ItemHistory(
  int ItemId,
  IReadOnlyList<ItemHistoryLog> History);
