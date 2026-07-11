using System.Net;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using Poe2scout.Models;
using Poe2scout.Repositories.League.Models;

namespace Poe2scout.UniquePriceLog.Worker;

public interface IPoeTradeClient
{
  Task<TradeSearchResponse> SearchUniqueAsync(
    UniqueItem uniqueItem,
    League league,
    string currency,
    CancellationToken cancellationToken);

  Task<TradeSearchResponse> SearchCurrencyAsync(
    CurrencyItem currencyItem,
    League league,
    CancellationToken cancellationToken);

  Task<TradeFetchResponse> FetchAsync(
    IReadOnlyList<string> itemIds,
    string queryId,
    CancellationToken cancellationToken);
}

public sealed class PoeTradeClient(
  HttpClient httpClient,
  Func<TimeSpan, CancellationToken, Task>? delay = null) : IPoeTradeClient
{
  private const string BaseUrl = "https://www.pathofexile.com/api/trade2";
  private const string Realm = "poe2";
  private const string UserAgent = "POE2SCOUT (contact: b@girardet.co.nz)";
  private const int MaxRetries = 5;
  private static readonly TimeSpan PostDelay = TimeSpan.FromSeconds(17);
  private static readonly TimeSpan GetDelay = TimeSpan.FromSeconds(3);
  private static readonly TimeSpan RetryDelay = TimeSpan.FromSeconds(300);
  private static readonly JsonSerializerOptions JsonOptions = new()
  {
    PropertyNameCaseInsensitive = true,
    NumberHandling = JsonNumberHandling.AllowReadingFromString
  };

  public async Task<TradeSearchResponse> SearchUniqueAsync(
    UniqueItem uniqueItem,
    League league,
    string currency,
    CancellationToken cancellationToken)
  {
    var query = CreateUniqueQuery(uniqueItem, currency);
    try
    {
      return await PostSearch(query, league.Value, cancellationToken);
    }
    catch (TradeClientException exception) when (exception.IsUnknownItemName)
    {
      throw new UniqueItemDelistedException(uniqueItem.UniqueItemId, uniqueItem.Name, exception);
    }
  }

  public Task<TradeSearchResponse> SearchCurrencyAsync(
    CurrencyItem currencyItem,
    League league,
    CancellationToken cancellationToken)
    => PostSearch(CreateCurrencyQuery(currencyItem), league.Value, cancellationToken);

  public async Task<TradeFetchResponse> FetchAsync(
    IReadOnlyList<string> itemIds,
    string queryId,
    CancellationToken cancellationToken)
  {
    var ids = string.Join(',', itemIds);
    var url = $"{BaseUrl}/fetch/{ids}?query={Uri.EscapeDataString(queryId)}&realm={Realm}";
    using var response = await SendAsync(HttpMethod.Get, url, null, cancellationToken);
    await using var body = await response.Content.ReadAsStreamAsync(cancellationToken);
    return await JsonSerializer.DeserializeAsync<TradeFetchResponse>(body, JsonOptions, cancellationToken)
           ?? throw new InvalidOperationException("Trade fetch API returned an empty response.");
  }

  private async Task<TradeSearchResponse> PostSearch(
    object query,
    string league,
    CancellationToken cancellationToken)
  {
    var url = $"{BaseUrl}/search/{Realm}/{Uri.EscapeDataString(league)}";
    var content = JsonSerializer.Serialize(query, JsonOptions);
    using var response = await SendAsync(HttpMethod.Post, url, content, cancellationToken);
    await using var body = await response.Content.ReadAsStreamAsync(cancellationToken);
    return await JsonSerializer.DeserializeAsync<TradeSearchResponse>(body, JsonOptions, cancellationToken)
           ?? throw new InvalidOperationException("Trade search API returned an empty response.");
  }

  private async Task<HttpResponseMessage> SendAsync(
    HttpMethod method,
    string url,
    string? content,
    CancellationToken cancellationToken)
  {
    for (var attempt = 1; attempt <= MaxRetries; attempt++)
    {
      await Delay(method == HttpMethod.Post ? PostDelay : GetDelay, cancellationToken);

      using var request = new HttpRequestMessage(method, url)
      {
        Content = content is null
          ? null
          : new StringContent(content, Encoding.UTF8, "application/json")
      };
      request.Headers.UserAgent.ParseAdd(UserAgent);
      var response = await httpClient.SendAsync(request, cancellationToken);

      if (response.StatusCode == HttpStatusCode.OK)
      {
        return response;
      }

      var statusCode = response.StatusCode;
      var body = await response.Content.ReadAsStringAsync(cancellationToken);
      if (statusCode is HttpStatusCode.Forbidden
          or HttpStatusCode.MethodNotAllowed
          or HttpStatusCode.ServiceUnavailable)
      {
        response.Dispose();
        if (attempt < MaxRetries)
        {
          await Task.Delay(RetryDelay, cancellationToken);
          continue;
        }

        throw new TradeClientException(
          $"Max retries ({MaxRetries}) exceeded. Last status: {(int)statusCode}",
          statusCode,
          body);
      }

      response.Dispose();
      throw CreateException(statusCode, body);
    }

    throw new InvalidOperationException("Trade API retry loop completed unexpectedly.");
  }

  private Task Delay(TimeSpan duration, CancellationToken cancellationToken)
    => delay is null ? Task.Delay(duration, cancellationToken) : delay(duration, cancellationToken);

  private static TradeClientException CreateException(HttpStatusCode statusCode, string body)
  {
    var message = statusCode switch
    {
      HttpStatusCode.TooManyRequests => "Rate limit exceeded",
      >= HttpStatusCode.BadRequest and < HttpStatusCode.InternalServerError => "Client error occurred",
      >= HttpStatusCode.InternalServerError => "Server error occurred",
      _ => "Trade API request failed"
    };
    return new TradeClientException(
      $"{message} - Status Code: {(int)statusCode} | {body}",
      statusCode,
      body);
  }

  private static object CreateUniqueQuery(UniqueItem uniqueItem, string currency)
  {
    var filters = new Dictionary<string, object>
    {
      ["trade_filters"] = new
      {
        filters = new
        {
          price = new { option = currency }
        }
      }
    };

    if (uniqueItem.CategoryApiId != "jewel")
    {
      filters["misc_filters"] = new
      {
        filters = new
        {
          corrupted = new { option = "false" }
        }
      };
    }

    return new
    {
      query = new
      {
        status = new { option = "securable" },
        name = uniqueItem.Name,
        stats = new[] { new { type = "and", filters = Array.Empty<object>() } },
        filters
      },
      sort = new { price = "asc" }
    };
  }

  private static object CreateCurrencyQuery(CurrencyItem currencyItem)
    => new
    {
      query = new
      {
        status = new { option = "online" },
        type = currencyItem.Text,
        stats = new[] { new { type = "and", filters = Array.Empty<object>() } }
      },
      sort = new { price = "asc" }
    };
}

public sealed class TradeClientException(
  string message,
  HttpStatusCode statusCode,
  string responseBody) : Exception(message)
{
  public HttpStatusCode StatusCode { get; } = statusCode;
  public string ResponseBody { get; } = responseBody;
  public bool IsUnknownItemName
    => StatusCode == HttpStatusCode.BadRequest
       && Message.Contains("Unknown item name", StringComparison.Ordinal);
}

public sealed class UniqueItemDelistedException(
  int uniqueItemId,
  string itemName,
  Exception? innerException = null)
  : Exception($"Unique item '{itemName}' is currently delisted", innerException)
{
  public int UniqueItemId { get; } = uniqueItemId;
  public string ItemName { get; } = itemName;
}
