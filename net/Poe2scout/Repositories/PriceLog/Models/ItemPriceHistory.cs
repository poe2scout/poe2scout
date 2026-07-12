using Poe2scout.Models;

namespace Poe2scout.Repositories.PriceLog.Models;

public record ItemPriceHistory(
  IReadOnlyList<PriceLogEntry> PriceHistory,
  bool HasMore);
