namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record CurrencyExchangeHistory(
  Dictionary<string, bool> Meta,
  List<CurrencyExchangeHistoryEntry> Data);

public record CurrencyExchangeHistoryEntry(
  int Epoch,
  float MarketCap,
  float Volume);
