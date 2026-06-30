namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record PairHistoryEntryDataDetails(
  int CurrencyItemId,
  decimal ValueTraded,
  decimal RelativePrice,
  decimal StockValue,
  long VolumeTraded,
  long HighestStock);
    
