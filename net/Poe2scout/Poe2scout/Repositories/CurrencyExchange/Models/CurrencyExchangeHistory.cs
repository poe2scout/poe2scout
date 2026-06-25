namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record CurrencyExchangeHistory(
  Dictionary<string, bool> Meta,
  List<(int Epoch, float MarketCap, float Volume)> data);