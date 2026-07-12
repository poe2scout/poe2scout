using System.Text.Json;

namespace Poe2scout.ItemSync.Worker;

public interface IItemSyncClient
{
  Task<ItemFeedResponse> GetItemsAsync(string tradeIdentifier, CancellationToken cancellationToken);
  Task<CurrencyFeedResponse> GetCurrenciesAsync(string tradeIdentifier, CancellationToken cancellationToken);
}

public sealed class ItemSyncClient : IItemSyncClient
{
  private const string BaseUrl = "https://www.pathofexile.com/api";
  private const string UserAgent = "POE2SCOUT (contact: b@girardet.co.nz)";

  private readonly HttpClient httpClient;

  private static readonly JsonSerializerOptions JsonOptions = new()
  {
    PropertyNameCaseInsensitive = true
  };

  public ItemSyncClient(HttpClient httpClient)
  {
    this.httpClient = httpClient;
    httpClient.DefaultRequestHeaders.TryAddWithoutValidation("User-Agent", UserAgent);
  }

  public Task<ItemFeedResponse> GetItemsAsync(
    string tradeIdentifier,
    CancellationToken cancellationToken)
    => GetAsync<ItemFeedResponse>(
      $"{BaseUrl}/{tradeIdentifier}/data/items",
      ValidateItems,
      cancellationToken);

  public Task<CurrencyFeedResponse> GetCurrenciesAsync(
    string tradeIdentifier,
    CancellationToken cancellationToken)
    => GetAsync<CurrencyFeedResponse>(
      $"{BaseUrl}/{tradeIdentifier}/data/static",
      ValidateCurrencies,
      cancellationToken);

  private async Task<T> GetAsync<T>(
    string url,
    Func<T, T> validate,
    CancellationToken cancellationToken)
  {
    using var response = await httpClient.GetAsync(url, cancellationToken);
    response.EnsureSuccessStatusCode();

    await using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
    var payload = await JsonSerializer.DeserializeAsync<T>(stream, JsonOptions, cancellationToken)
                  ?? throw new JsonException("POE API returned an empty response.");
    return validate(payload);
  }

  private static ItemFeedResponse ValidateItems(ItemFeedResponse response)
  {
    if (response.Result is null)
    {
      throw new JsonException("POE item response did not contain a result.");
    }

    foreach (var category in response.Result)
    {
      if (category.Id is null || category.Label is null || category.Entries is null)
      {
        throw new JsonException("POE item response contained an incomplete category.");
      }

      foreach (var entry in category.Entries)
      {
        if (entry.Type is null)
        {
          throw new JsonException("POE item response contained an item without a type.");
        }
      }
    }

    return response;
  }

  private static CurrencyFeedResponse ValidateCurrencies(CurrencyFeedResponse response)
  {
    if (response.Result is null)
    {
      throw new JsonException("POE currency response did not contain a result.");
    }

    foreach (var category in response.Result)
    {
      if (category.Id is null || category.Entries is null)
      {
        throw new JsonException("POE currency response contained an incomplete category.");
      }

      foreach (var entry in category.Entries)
      {
        if (entry.Id is null || entry.Text is null)
        {
          throw new JsonException("POE currency response contained an incomplete entry.");
        }
      }
    }

    return response;
  }
}
