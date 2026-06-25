namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record PairHistoryEntryDataDetails(
  int CurrencyItemId,
  double ValueTraded,
  double RelativePrice,
  double StockValue,
  int VolumeTraded,
  int HighestStock);
    