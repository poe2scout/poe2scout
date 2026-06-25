namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record PairHistoryEntry(
  int Epoch,
  PairHistoryEntryData Data);