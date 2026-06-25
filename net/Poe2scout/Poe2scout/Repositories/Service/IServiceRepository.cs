using Poe2scout.Repositories.Service.Models;

namespace Poe2scout.Repositories.Service;

public interface IServiceRepository
{
  public Task<bool> GetCurrencyFetchStatus(DateTime startTime);
  public Task<IReadOnlyList<int>> GetFetchedItemIds(string currentHour, int leagueId);
  public Task<ServiceCacheValue> GetServiceCacheValue(string serviceName);
  public Task SetServiceCacheValue(string serviceName, int value);
}
