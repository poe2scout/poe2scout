using System.Collections.Concurrent;
using System.Diagnostics.CodeAnalysis;
using Poe2scout.Api.Handlers.Items;

namespace Poe2scout.Api;

public class ItemsCache : ConcurrentDictionary<(string leagueName, string realm), (List<GetHandler.GetItemResponse> Items, DateTime ExpiresUtc)>
{
  public bool TryGetCache(string leagueName, string realm, [NotNullWhen(true)] out List<GetHandler.GetItemResponse>? itemsResponse)
  {
    if (TryGetValue((leagueName, realm), out var cacheEntry))
    {
      if (cacheEntry.ExpiresUtc > DateTime.UtcNow)
      {
        itemsResponse = cacheEntry.Items;
        return true;
      }
    }
    
    itemsResponse = null;
    return false;
  }

  public void SetCache(string leagueName, string realm, List<GetHandler.GetItemResponse> itemsResponse)
  {
    this[(leagueName, realm)] = (itemsResponse, DateTime.UtcNow.AddMinutes(15));
  }
}