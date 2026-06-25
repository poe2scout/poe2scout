using Poe2scout.Repositories.CurrencyExchange.Models;

namespace Poe2scout.Repositories.CurrencyExchange;

public interface ICurrencyExchangeRepository
{
  public Task<int?> CreateSnapshot(CurrencyExchangeSnapshot snapshot);
  public Task<CurrencyExchangeHistory> GetCurrencyExchangeHistory(int leagueId, int realmId, int endTime, int limit);
  public Task<IReadOnlyList<SnapshotPair>> GetCurrentSnapshotPairs(int leagueId, int realmId);
  public Task<CurrencyExchangeData> GetCurrencyExchange(int leagueId, int realmId);
  public Task<IReadOnlyList<int>> GetExistingSnapshotLeagueIds(int epoch, int realmId);
  public Task<PairHistory> GetPairHistory(int leagueId, int realmId, int currencyOneId, int currencyTwoId, int end_epoch, int limit);
  public Task UpdatePairHistories();
}