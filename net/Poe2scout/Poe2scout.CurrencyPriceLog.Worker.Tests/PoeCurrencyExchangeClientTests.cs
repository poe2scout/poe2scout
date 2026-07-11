using System.Net;
using System.Text;

namespace Poe2scout.CurrencyPriceLog.Worker.Tests;

public class PoeCurrencyExchangeClientTests
{
  [Fact]
  public async Task AcquiresTokenCachesItAndUsesRealmSpecificUrls()
  {
    var handler = new QueueHandler([
      _ => Json(HttpStatusCode.OK, """{"access_token":"token-one"}"""),
      _ => Json(HttpStatusCode.OK, SnapshotJson),
      _ => Json(HttpStatusCode.OK, SnapshotJson)
    ]);
    var client = CreateClient(handler);

    var pc = await client.GetSnapshot("pc", 123, CancellationToken.None);
    await client.GetSnapshot("xbox", 456, CancellationToken.None);

    Assert.Equal(124, pc.NextChangeId);
    var pair = Assert.Single(pc.Markets);
    Assert.Equal("exalted|chaos", pair.MarketId);
    Assert.Equal(100, pair.VolumeTraded["chaos"]);
    Assert.Equal(20, pair.HighestStock["chaos"]);
    Assert.Equal("https://www.pathofexile.com/oauth/token", handler.Requests[0].Url);
    Assert.Contains("grant_type=client_credentials", handler.Requests[0].Body);
    Assert.Contains("scope=service%3Acxapi", handler.Requests[0].Body);
    Assert.Equal("https://www.pathofexile.com/api/currency-exchange/123", handler.Requests[1].Url);
    Assert.Equal("https://www.pathofexile.com/api/currency-exchange/xbox/456", handler.Requests[2].Url);
    Assert.All(handler.Requests.Skip(1), request =>
    {
      Assert.Equal("Bearer token-one", request.Authorization);
      Assert.Equal("OAuth client-id/1.0.0 (contact: b@girardet.co.nz)", request.UserAgent);
    });
  }

  [Fact]
  public async Task RefreshesTokenOnceAfterUnauthorizedResponse()
  {
    var handler = new QueueHandler([
      _ => Json(HttpStatusCode.OK, """{"access_token":"token-one"}"""),
      _ => new HttpResponseMessage(HttpStatusCode.Unauthorized),
      _ => Json(HttpStatusCode.OK, """{"access_token":"token-two"}"""),
      _ => Json(HttpStatusCode.OK, SnapshotJson)
    ]);
    var client = CreateClient(handler);

    await client.GetSnapshot("pc", 123, CancellationToken.None);

    Assert.Equal("Bearer token-one", handler.Requests[1].Authorization);
    Assert.Equal("Bearer token-two", handler.Requests[3].Authorization);
    Assert.Equal(2, handler.Requests.Count(request => request.Url.EndsWith("/oauth/token")));
  }

  [Theory]
  [InlineData(HttpStatusCode.TooManyRequests)]
  [InlineData(HttpStatusCode.BadRequest)]
  [InlineData(HttpStatusCode.InternalServerError)]
  public async Task DoesNotRetryOtherFailureStatuses(HttpStatusCode statusCode)
  {
    var handler = new QueueHandler([
      _ => Json(HttpStatusCode.OK, """{"access_token":"token"}"""),
      _ => new HttpResponseMessage(statusCode)
    ]);
    var client = CreateClient(handler);

    var exception = await Assert.ThrowsAsync<PoeApiException>(
      () => client.GetSnapshot("pc", 123, CancellationToken.None));

    Assert.Equal(statusCode, exception.StatusCode);
  }

  private static PoeCurrencyExchangeClient CreateClient(QueueHandler handler)
    => new(new HttpClient(handler), TestConfig.Create());

  private static HttpResponseMessage Json(HttpStatusCode statusCode, string json)
    => new(statusCode) { Content = new StringContent(json, Encoding.UTF8, "application/json") };

  private const string SnapshotJson = """
    {
      "next_change_id": 124,
      "markets": [
        {
          "league": "Test League",
          "market_id": "exalted|chaos",
          "volume_traded": { "exalted": 10, "chaos": 100 },
          "highest_stock": { "exalted": 5, "chaos": 20 }
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
        request.Method,
        request.Headers.Authorization?.ToString(),
        request.Headers.UserAgent.ToString(),
        request.Content is null ? string.Empty : await request.Content.ReadAsStringAsync(cancellationToken));
      Requests.Add(snapshot);
      return responseQueue.Dequeue()(snapshot);
    }
  }

  private sealed record RequestSnapshot(
    string Url,
    HttpMethod Method,
    string? Authorization,
    string UserAgent,
    string Body);
}
