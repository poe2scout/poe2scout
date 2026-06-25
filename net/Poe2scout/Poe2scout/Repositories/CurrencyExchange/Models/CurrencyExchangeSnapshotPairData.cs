namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record CurrencyExchangeSnapshotPairData(
  double ValueTraded,
  double RelativePrice,
  int VolumeTraded,
  int HighestStock,
  double StockValue);