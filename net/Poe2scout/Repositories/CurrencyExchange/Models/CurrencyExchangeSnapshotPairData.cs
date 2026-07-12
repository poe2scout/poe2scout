namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record CurrencyExchangeSnapshotPairData(
  decimal ValueTraded,
  decimal RelativePrice,
  long VolumeTraded,
  long HighestStock,
  decimal StockValue);
