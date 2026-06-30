namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record PairData(
  decimal ValueTraded,
  decimal RelativePrice,
  decimal StockValue,
  long VolumeTraded,
  long HighestStock);
