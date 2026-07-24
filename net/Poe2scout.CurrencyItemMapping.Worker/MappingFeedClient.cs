using System.Text.Json;
using Poe2scout.Repositories.Realm.Models;

namespace Poe2scout.CurrencyItemMapping.Worker;

public interface IMappingFeedClient
{
  Task<IReadOnlyList<BaseItemCandidate>> GetBaseItems(
    string gameApiId,
    CancellationToken cancellationToken);

  Task<IReadOnlySet<string>> GetCurrentTradeApiIds(
    string tradeIdentifier,
    CancellationToken cancellationToken);

  Task<IReadOnlySet<string>> GetCdnBaseItemTypeIds(
    IReadOnlyList<Realm> realms,
    int epoch,
    CancellationToken cancellationToken);
}

public sealed class MappingFeedClient(
  HttpClient httpClient,
  CurrencyItemMappingConfig config) : IMappingFeedClient
{
  private const string TradeApiBaseUrl = "https://www.pathofexile.com/api";
  private const string CdnBaseUrl = "https://web.poecdn.com/api/currency-exchange";
  private static readonly HashSet<string> NonExchangeTradeCategories =
    new HashSet<string>(StringComparer.Ordinal)
    {
      "MapKey",
      "MapsSpecial",
      "MapsUnique",
      "Waystones"
    };
  
  private static readonly JsonSerializerOptions JsonOptions = new()
  {
    PropertyNameCaseInsensitive = true
  };

  private readonly SemaphoreSlim rePoeLock = new(1, 1);
  private readonly Dictionary<string, CachedBaseItems> rePoeCache = [];

  public async Task<IReadOnlyList<BaseItemCandidate>> GetBaseItems(
    string gameApiId,
    CancellationToken cancellationToken)
  {
    await rePoeLock.WaitAsync(cancellationToken);
    try
    {
      if (rePoeCache.TryGetValue(gameApiId, out var cached)
          && cached.ExpiresAt > DateTimeOffset.UtcNow)
      {
        return cached.Items;
      }

      var path = gameApiId == "poe2" ? "poe2/base_items.json" : "base_items.json";
      using var response = await SendGet($"{config.RePoeBaseUrl}/{path}", cancellationToken);
      response.EnsureSuccessStatusCode();

      await using var body = await response.Content.ReadAsStreamAsync(cancellationToken);
      using var document = await JsonDocument.ParseAsync(body, cancellationToken: cancellationToken);
      if (document.RootElement.ValueKind != JsonValueKind.Object)
      {
        throw new JsonException("RePoE base_items.json root was not an object.");
      }

      var items = new List<BaseItemCandidate>();
      foreach (var property in document.RootElement.EnumerateObject())
      {
        if (!property.Value.TryGetProperty("name", out var nameElement)
            || nameElement.ValueKind != JsonValueKind.String
            || string.IsNullOrWhiteSpace(nameElement.GetString()))
        {
          continue;
        }

        items.Add(new BaseItemCandidate(property.Name, nameElement.GetString()!));
      }

      if (items.Count == 0)
      {
        throw new JsonException("RePoE base_items.json contained no items.");
      }

      rePoeCache[gameApiId] = new CachedBaseItems(
        items,
        DateTimeOffset.UtcNow.AddHours(config.RePoeRefreshHours));
      return items;
    }
    finally
    {
      rePoeLock.Release();
    }
  }

  public async Task<IReadOnlySet<string>> GetCurrentTradeApiIds(
    string tradeIdentifier,
    CancellationToken cancellationToken)
  {
    using var response = await SendGet($"{TradeApiBaseUrl}/{tradeIdentifier}/data/static", cancellationToken);
    response.EnsureSuccessStatusCode();

    await using var body = await response.Content.ReadAsStreamAsync(cancellationToken);
    var payload = await JsonSerializer.DeserializeAsync<TradeStaticResponse>(
                    body,
                    JsonOptions,
                    cancellationToken) ?? throw new JsonException("Trade-static feed returned an empty response.");
    
    if (payload.Result is null)
    {
      throw new JsonException("Trade-static feed did not contain a result.");
    }

    var identifiers = new HashSet<string>(StringComparer.Ordinal);
    foreach (var category in payload.Result)
    {
      if (category.Id is null || category.Entries is null)
      {
        throw new JsonException("Trade-static feed contained an incomplete category.");
      }

      if (NonExchangeTradeCategories.Contains(category.Id))
      {
        continue;
      }

      foreach (var entry in category.Entries)
      {
        if (string.IsNullOrWhiteSpace(entry.Id))
        {
          throw new JsonException("Trade-static feed contained an incomplete currency entry.");
        }

        if (entry.Id == "sep")
        {
          continue;
        }

        if (string.IsNullOrWhiteSpace(entry.Text))
        {
          throw new JsonException("Trade-static feed contained an incomplete currency entry.");
        }

        identifiers.Add(entry.Id);
      }
    }

    return identifiers.Count == 0 ? throw new JsonException("Trade-static feed contained no currency identifiers.") : identifiers;
  }

  public async Task<IReadOnlySet<string>> GetCdnBaseItemTypeIds(
    IReadOnlyList<Realm> realms,
    int epoch,
    CancellationToken cancellationToken)
  {
    var snapshots = await Task.WhenAll(realms.Select(async realm =>
    {
      var realmPath = realm.ApiId == "pc" ? string.Empty : $"/{realm.ApiId}";
      using var response = await SendGet(
        $"{CdnBaseUrl}{realmPath}/{epoch}",
        cancellationToken);
      response.EnsureSuccessStatusCode();

      await using var body = await response.Content.ReadAsStreamAsync(cancellationToken);
      return await JsonSerializer.DeserializeAsync<CdnExchangeResponse>(
               body,
               JsonOptions,
               cancellationToken)
             ?? throw new JsonException($"CDN feed for {realm.ApiId} returned an empty response.");
    }));

    var identifiers = new HashSet<string>(StringComparer.Ordinal);
    foreach (var (snapshot, realm) in snapshots.Zip(realms))
    {
      if (snapshot.Markets is null)
      {
        throw new JsonException($"CDN feed for {realm.ApiId} did not contain markets.");
      }

      foreach (var market in snapshot.Markets)
      {
        identifiers.UnionWith(market.MarketPair);
      }
    }

    return identifiers;
  }

  private async Task<HttpResponseMessage> SendGet(
    string url,
    CancellationToken cancellationToken)
  {
    using var request = new HttpRequestMessage(HttpMethod.Get, url);
    request.Headers.UserAgent.ParseAdd("Poe2scout/1.0.0 (contact: b@girardet.co.nz)");
    return await httpClient.SendAsync(request, cancellationToken);
  }

  private sealed record CachedBaseItems(
    IReadOnlyList<BaseItemCandidate> Items,
    DateTimeOffset ExpiresAt);
}
