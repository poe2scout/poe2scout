using System.Net;
using System.Text;
using Poe2scout.CurrencyExchange.Worker;

namespace Poe2scout.CurrencyExchange.Worker.Tests;

public class CurrencyExchangeClientTests
{
  [Fact]
  public async Task BuildsCdnRealmUrlsWithoutOAuth()
  {
    var delays = new List<TimeSpan>();
    var handler = new QueueHandler(
    [
      _ => Json(HttpStatusCode.OK, SnapshotJson),
      _ => Json(HttpStatusCode.OK, SnapshotJson),
      _ => Json(HttpStatusCode.OK, SnapshotJson)
    ]);
    var client = CreateClient(handler, delays);

    await client.GetSnapshot("pc", null, CancellationToken.None);
    await client.GetSnapshot("pc", 123, CancellationToken.None);
    await client.GetSnapshot("xbox", 456, CancellationToken.None);

    Assert.Equal("https://web.poecdn.com/api/currency-exchange", handler.Requests[0].Url);
    Assert.Equal("https://web.poecdn.com/api/currency-exchange/123", handler.Requests[1].Url);
    Assert.Equal("https://web.poecdn.com/api/currency-exchange/xbox/456", handler.Requests[2].Url);
    Assert.DoesNotContain(handler.Requests, request => request.Url.Contains("oauth"));
    Assert.All(handler.Requests, request =>
    {
      Assert.Null(request.Authorization);
      Assert.Equal("Poe2scout/1.0.0 (contact: b@girardet.co.nz)", request.UserAgent);
    });
    Assert.Empty(delays);
  }

  [Theory]
  [InlineData(HttpStatusCode.TooManyRequests)]
  [InlineData(HttpStatusCode.BadRequest)]
  [InlineData(HttpStatusCode.InternalServerError)]
  public async Task DoesNotRetryNonRetryableStatuses(HttpStatusCode statusCode)
  {
    var handler = new QueueHandler(
    [
      _ => new HttpResponseMessage(statusCode)
    ]);
    var client = CreateClient(handler);

    var exception = await Assert.ThrowsAsync<PoeCurrencyExchangeException>(
      () => client.GetSnapshot("pc", 123, CancellationToken.None));

    Assert.Equal(statusCode, exception.StatusCode);
    Assert.Single(handler.Requests);
  }

  [Fact]
  public async Task RetriesServiceUnavailableAndFailsAfterMaximumAttempts()
  {
    var delays = new List<TimeSpan>();
    var responses = new List<Func<RequestSnapshot, HttpResponseMessage>>();
    responses.AddRange(Enumerable.Repeat<Func<RequestSnapshot, HttpResponseMessage>>(
      _ => new HttpResponseMessage(HttpStatusCode.ServiceUnavailable),
      5));
    var handler = new QueueHandler(responses);
    var client = CreateClient(handler, delays);

    var exception = await Assert.ThrowsAsync<PoeCurrencyExchangeException>(
      () => client.GetSnapshot("pc", 123, CancellationToken.None));

    Assert.Equal(HttpStatusCode.ServiceUnavailable, exception.StatusCode);
    Assert.Equal(5, handler.Requests.Count);
    Assert.Equal(
      Enumerable.Repeat(TimeSpan.FromMinutes(5), 4),
      delays);
  }

  private static PoeCurrencyExchangeClient CreateClient(
    QueueHandler handler,
    List<TimeSpan>? delays = null)
    => new(
      new HttpClient(handler),
      (duration, _) =>
      {
        delays?.Add(duration);
        return Task.CompletedTask;
      });

  private static HttpResponseMessage Json(HttpStatusCode statusCode, string json)
    => new(statusCode)
    {
      Content = new StringContent(json, Encoding.UTF8, "application/json")
    };

  private const string SnapshotJson = """
    {
      "next_change_id": 124,
      "markets": [
        {
          "league": "Test League",
          "market_id": "exalted|chaos",
          "market_pair": ["Metadata/Items/Currency/ExaltedOrb", "Metadata/Items/Currency/CurrencyRerollRare"],
          "volume_traded": {
            "Metadata/Items/Currency/ExaltedOrb": 10,
            "Metadata/Items/Currency/CurrencyRerollRare": 100
          },
          "highest_stock": {
            "Metadata/Items/Currency/ExaltedOrb": 5,
            "Metadata/Items/Currency/CurrencyRerollRare": 20
          }
        }
      ]
    }
    """;

  private sealed class QueueHandler(
    IEnumerable<Func<RequestSnapshot, HttpResponseMessage>> responses) : HttpMessageHandler
  {
    private readonly Queue<Func<RequestSnapshot, HttpResponseMessage>> responseQueue = new(responses);
    public List<RequestSnapshot> Requests { get; } = [];

    protected override async Task<HttpResponseMessage> SendAsync(
      HttpRequestMessage request,
      CancellationToken cancellationToken)
    {
      var snapshot = new RequestSnapshot(
        request.RequestUri!.ToString(),
        request.Headers.Authorization?.ToString(),
        request.Headers.UserAgent.ToString(),
        request.Content is null
          ? string.Empty
          : await request.Content.ReadAsStringAsync(cancellationToken));
      Requests.Add(snapshot);
      return responseQueue.Dequeue()(snapshot);
    }
  }

  private sealed record RequestSnapshot(
    string Url,
    string? Authorization,
    string UserAgent,
    string Body);
}
