namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record CurrencyExchangeSnapshot(
  int Epoch,
  int LeagueId,
  int RealmId,
  List<CurrencyExchangeSnapshotPair> Pairs,
  decimal Volume,
  decimal MarketCap);
