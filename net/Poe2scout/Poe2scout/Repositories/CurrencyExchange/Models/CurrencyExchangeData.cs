namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record CurrencyExchangeData(
  int Epoch,
  double Volume,
  double MarketCap);