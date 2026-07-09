namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record CurrencyExchangeSnapshotPair(
  int CurrencyOneItemId,
  int CurrencyTwoItemId,
  decimal Volume,
  CurrencyExchangeSnapshotPairData CurrencyOneData,
  CurrencyExchangeSnapshotPairData CurrencyTwoData);
