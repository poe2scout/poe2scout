namespace Poe2scout.Repositories.CurrencyExchange.Models;

public record PairHistoryEntryData(
  PairHistoryEntryDataDetails CurrencyOneData,
  PairHistoryEntryDataDetails CurrencyTwoData);