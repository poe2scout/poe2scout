using System.Net;
using System.Text.Json;

namespace Poe2scout.CurrencyExchange.Worker;

public interface ICurrencyExchangeClient
{
  Task<CurrencyExchangeResponse> GetSnapshot(
    string realmApiId,
    int? epoch,
    CancellationToken cancellationToken);
}

public sealed class PoeCurrencyExchangeClient(
  HttpClient httpClient,
  Func<TimeSpan, CancellationToken, Task>? delay = null) : ICurrencyExchangeClient
{
  private const string BaseUrl = "https://web.poecdn.com/api/currency-exchange";
  private const int MaxAttempts = 5;
  private static readonly TimeSpan RetryDelay = TimeSpan.FromMinutes(5);
  public async Task<CurrencyExchangeResponse> GetSnapshot(
    string realmApiId,
    int? epoch,
    CancellationToken cancellationToken)
  {
    var url = BuildSnapshotUrl(realmApiId, epoch);

    for (var attempt = 1; attempt <= MaxAttempts; attempt++)
    {
      using var response = await SendGet(url, cancellationToken);

      if (response.StatusCode == HttpStatusCode.OK)
      {
        await using var body = await response.Content.ReadAsStreamAsync(cancellationToken);
        var result = await JsonSerializer.DeserializeAsync<CurrencyExchangeResponse>(
                       body,
                       cancellationToken: cancellationToken)
                     ?? throw new InvalidOperationException(
                       "Currency exchange API returned an empty response.");
        return result;
      }

      if (IsRetryable(response.StatusCode))
      {
        if (attempt < MaxAttempts)
        {
          await Delay(RetryDelay, cancellationToken);
          continue;
        }

        throw new PoeCurrencyExchangeException(
          $"Max retries ({MaxAttempts}) exceeded. Last status: {(int)response.StatusCode}",
          response.StatusCode);
      }

      throw CreateStatusException(response.StatusCode);
    }

    throw new InvalidOperationException("The retry loop completed unexpectedly.");
  }

  private static string BuildSnapshotUrl(string realmApiId, int? epoch)
  {
    var suffix = realmApiId == "pc"
      ? epoch is null ? string.Empty : $"/{epoch.Value}"
      : epoch is null
        ? $"/{realmApiId}"
        : $"/{realmApiId}/{epoch.Value}";

    return $"{BaseUrl}{suffix}";
  }

  private async Task<HttpResponseMessage> SendGet(
    string url,
    CancellationToken cancellationToken)
  {
    using var request = new HttpRequestMessage(HttpMethod.Get, url);
    request.Headers.UserAgent.ParseAdd(
      "Poe2scout/1.0.0 (contact: b@girardet.co.nz)");
    return await httpClient.SendAsync(request, cancellationToken);
  }

  private Task Delay(TimeSpan duration, CancellationToken cancellationToken)
    => delay is null ? Task.Delay(duration, cancellationToken) : delay(duration, cancellationToken);

  private static bool IsRetryable(HttpStatusCode statusCode)
    => statusCode is HttpStatusCode.Forbidden
      or HttpStatusCode.MethodNotAllowed
      or HttpStatusCode.ServiceUnavailable;

  private static PoeCurrencyExchangeException CreateStatusException(HttpStatusCode statusCode)
  {
    var message = statusCode switch
    {
      HttpStatusCode.TooManyRequests => "Rate limit exceeded",
      >= HttpStatusCode.BadRequest and < HttpStatusCode.InternalServerError => "Client error occurred",
      >= HttpStatusCode.InternalServerError => "Server error occurred",
      _ => "GetFromApiFailure"
    };

    return new PoeCurrencyExchangeException(
      $"{message} - Status Code: {(int)statusCode}",
      statusCode);
  }

}

public sealed class PoeCurrencyExchangeException(
  string message,
  HttpStatusCode statusCode) : Exception(message)
{
  public HttpStatusCode StatusCode { get; } = statusCode;
}
