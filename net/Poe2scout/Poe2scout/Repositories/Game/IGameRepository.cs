using Poe2scout.Repositories.Game.Models;

namespace Poe2scout.Repositories.Game;

public interface IGameRepository
{
  public Task<IReadOnlyList<BridgeCurrency>> GetBridgeCurrencies(int gameId);
  public Task<int> GetDefaultLeague(int gameId);
  public Task<IReadOnlyList<Models.Game>> GetGames();
}
