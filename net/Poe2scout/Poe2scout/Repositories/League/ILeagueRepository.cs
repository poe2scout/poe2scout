using Poe2scout.Repositories.League.Models;

namespace Poe2scout.Repositories.League;

public interface ILeagueRepository
{
  public Task<IReadOnlyList<int>> GetItemsInCurrentLeague(int leagueId, int realmId);
  public Task<Models.League?> GetLeagueByValue(string value, int gameId);
  public Task<IReadOnlyList<Models.League>> GetLeagues(int gameId);
  public Task<IReadOnlyList<Models.League>> GetCurrentLeagues(int gameId);
  public Task<Models.League> GetLeague(int leagueId);
}
