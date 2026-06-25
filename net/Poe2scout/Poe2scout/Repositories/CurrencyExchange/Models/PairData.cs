namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record PairData(
  double ValueTraded,
  double RelativePrice,
  double StockValue,
  int VolumeTraded,
  int HighestStock);