using System.Net;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Poe2scout.CurrencyPriceLog.Worker;

public interface IPoeCurrencyExchangeClient
{
  Task<CurrencyExchangeResponse> GetSnapshot(
    string realmApiId,
    int epoch,
    CancellationToken cancellationToken);
}

public sealed class PoeCurrencyExchangeClient(
  HttpClient httpClient,
  CurrencyPriceLogConfig config) : IPoeCurrencyExchangeClient
{
  private const int MaxAttempts = 5;
  private static readonly TimeSpan RequestDelay = TimeSpan.FromSeconds(3);
  private static readonly TimeSpan RetryDelay = TimeSpan.FromSeconds(300);
  private readonly SemaphoreSlim tokenLock = new(1, 1);
  private string? accessToken;

  public async Task<CurrencyExchangeResponse> GetSnapshot(
    string realmApiId,
    int epoch,
    CancellationToken cancellationToken)
  {
    var url = realmApiId == "pc"
      ? $"https://www.pathofexile.com/api/currency-exchange/{epoch}"
      : $"https://www.pathofexile.com/api/currency-exchange/{realmApiId}/{epoch}";

    for (var attempt = 1; attempt <= MaxAttempts; attempt++)
    {
      await Task.Delay(RequestDelay, cancellationToken);
      using var response = await SendAuthenticatedGet(url, cancellationToken);
      if (response.StatusCode == HttpStatusCode.OK)
      {
        await using var body = await response.Content.ReadAsStreamAsync(cancellationToken);
        return await JsonSerializer.DeserializeAsync<CurrencyExchangeResponse>(
                 body,
                 cancellationToken: cancellationToken)
               ?? throw new InvalidOperationException("Currency exchange API returned an empty response.");
      }

      if (IsRetryable(response.StatusCode))
      {
        if (attempt < MaxAttempts)
        {
          await Task.Delay(RetryDelay, cancellationToken);
          continue;
        }

        throw new PoeApiException(
          $"Max retries ({MaxAttempts}) exceeded. Last status: {(int)response.StatusCode}",
          response.StatusCode);
      }

      throw CreateStatusException(response.StatusCode);
    }

    throw new InvalidOperationException("The retry loop completed unexpectedly.");
  }

  private async Task<HttpResponseMessage> SendAuthenticatedGet(
    string url,
    CancellationToken cancellationToken)
  {
    var token = await GetAccessToken(cancellationToken);
    var response = await SendGet(url, token, cancellationToken);
    if (response.StatusCode != HttpStatusCode.Unauthorized)
    {
      return response;
    }

    response.Dispose();
    token = await RefreshAccessToken(token, cancellationToken);
    return await SendGet(url, token, cancellationToken);
  }

  private async Task<HttpResponseMessage> SendGet(
    string url,
    string token,
    CancellationToken cancellationToken)
  {
    using var request = new HttpRequestMessage(HttpMethod.Get, url);
    request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
    request.Headers.UserAgent.ParseAdd(
      $"OAuth {config.PoeApiClientId}/1.0.0 (contact: b@girardet.co.nz)");
    return await httpClient.SendAsync(request, cancellationToken);
  }

  private async Task<string> GetAccessToken(CancellationToken cancellationToken)
  {
    if (accessToken is not null)
    {
      return accessToken;
    }

    await tokenLock.WaitAsync(cancellationToken);
    try
    {
      accessToken ??= await RequestAccessToken(cancellationToken);
      return accessToken;
    }
    finally
    {
      tokenLock.Release();
    }
  }

  private async Task<string> RefreshAccessToken(
    string rejectedToken,
    CancellationToken cancellationToken)
  {
    await tokenLock.WaitAsync(cancellationToken);
    try
    {
      if (accessToken == rejectedToken)
      {
        accessToken = await RequestAccessToken(cancellationToken);
      }

      return accessToken ??= await RequestAccessToken(cancellationToken);
    }
    finally
    {
      tokenLock.Release();
    }
  }

  private async Task<string> RequestAccessToken(CancellationToken cancellationToken)
  {
    if (string.IsNullOrEmpty(config.PoeApiClientId) || string.IsNullOrEmpty(config.PoeApiClientSecret))
    {
      throw new InvalidOperationException("Path of Exile API credentials are required.");
    }

    using var request = new HttpRequestMessage(
      HttpMethod.Post,
      "https://www.pathofexile.com/oauth/token");
    request.Headers.UserAgent.ParseAdd("Poe2scout (b@girardet.co.nz)");
    request.Content = new FormUrlEncodedContent(new Dictionary<string, string>
    {
      ["client_id"] = config.PoeApiClientId,
      ["client_secret"] = config.PoeApiClientSecret,
      ["grant_type"] = "client_credentials",
      ["scope"] = "service:cxapi"
    });

    using var response = await httpClient.SendAsync(request, cancellationToken);
    response.EnsureSuccessStatusCode();
    await using var body = await response.Content.ReadAsStreamAsync(cancellationToken);
    var token = await JsonSerializer.DeserializeAsync<AccessTokenResponse>(
      body,
      cancellationToken: cancellationToken);
    return token?.AccessToken
           ?? throw new InvalidOperationException("OAuth response did not include an access token.");
  }

  private static bool IsRetryable(HttpStatusCode statusCode)
    => statusCode is HttpStatusCode.Forbidden
      or HttpStatusCode.MethodNotAllowed
      or HttpStatusCode.ServiceUnavailable;

  private static PoeApiException CreateStatusException(HttpStatusCode statusCode)
  {
    var message = statusCode switch
    {
      HttpStatusCode.TooManyRequests => "Rate limit exceeded",
      >= HttpStatusCode.BadRequest and < HttpStatusCode.InternalServerError => "Client error occurred",
      >= HttpStatusCode.InternalServerError => "Server error occurred",
      _ => "GetFromApiFailure"
    };
    return new PoeApiException($"{message} - Status Code: {(int)statusCode}", statusCode);
  }

  private sealed record AccessTokenResponse(
    [property: JsonPropertyName("access_token")] string AccessToken);
}

public sealed class PoeApiException(string message, HttpStatusCode statusCode) : Exception(message)
{
  public HttpStatusCode StatusCode { get; } = statusCode;
}
