using Poe2scout.Models;

namespace Poe2scout.Api.Helpers;

public static class PriceHelper
{
  public static List<PriceLogEntry> ConvertPriceHistoryFromBase(
    IEnumerable<PriceLogEntry> history,
    IEnumerable<PriceLogEntry> referenceCurrencyHistory)
  {
    var referenceCurrencyHistoryLookup = referenceCurrencyHistory.ToDictionary(x => x.Time);

    var adjustedPriceHistory = new List<PriceLogEntry>();
    var lastReferencePrice = 0.0;

    foreach (var priceLog in history)
    {
      if (referenceCurrencyHistoryLookup.TryGetValue(priceLog.Time, out var referencePriceLog))
      {
        lastReferencePrice = referencePriceLog.Price;
      }

      if (lastReferencePrice == 0.0)
      {
        continue;
      }
      
      adjustedPriceHistory.Add(priceLog with { Price = priceLog.Price / lastReferencePrice });
    }

    return adjustedPriceHistory;
  }
}