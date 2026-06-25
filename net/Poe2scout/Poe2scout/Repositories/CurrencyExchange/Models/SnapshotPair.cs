using Poe2scout.Models;

namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record SnapshotPair(
  int CurrencyExchangeSnapshotPairId,
  int CurrencyExchangeSnapshotId,
  double Volume,
  Poe2scout.Models.CurrencyItem CurrencyOne,
  Poe2scout.Models.CurrencyItem CurrencyTwo,
  PairData CurrencyOneData,
  PairData CurrencyTwoData);
