using Poe2scout.Repositories.Realm.Models;

namespace Poe2scout.Repositories.Realm;

public interface IRealmRepository
{
  public Task<Models.Realm?> GetRealm(string apiId);
  public Task<IReadOnlyList<Models.Realm>> GetRealms();
}
