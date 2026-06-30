namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record CurrencyExchangeData(
  int Epoch,
  decimal Volume,
  decimal MarketCap);
