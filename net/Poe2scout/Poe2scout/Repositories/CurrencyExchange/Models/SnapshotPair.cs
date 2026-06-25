using Poe2scout.Models;

namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record SnapshotPair(
  int CurrencyExchangeSnapshotPairId,
  int CurrencyExchangeSnapshotId,
  double Volume,
  CurrencyItem CurrencyOne,
  CurrencyItem CurrencyTwo,
  PairData CurrencyOneData,
  PairData CurrencyTwoData);