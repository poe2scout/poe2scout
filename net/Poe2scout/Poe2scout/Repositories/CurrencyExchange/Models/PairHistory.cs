namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record PairHistory(
  List<PairHistoryEntry> History,
  Dictionary<string, object> meta);