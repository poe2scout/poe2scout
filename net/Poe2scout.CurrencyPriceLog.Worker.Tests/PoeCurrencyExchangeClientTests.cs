using System.Net;
using System.Text;

namespace Poe2scout.CurrencyPriceLog.Worker.Tests;

public class PoeCurrencyExchangeClientTests
{
  [Fact]
  public async Task UsesCdnBaseIdsAndMakesNoOAuthRequest()
  {
    var handler = new QueueHandler([
      _ => Json(HttpStatusCode.OK, SnapshotJson),
      _ => Json(HttpStatusCode.OK, SnapshotJson)
    ]);
    var client = CreateClient(handler);

    var pc = await client.GetSnapshot("pc", 123, CancellationToken.None);
    await client.GetSnapshot("xbox", 456, CancellationToken.None);

    Assert.Equal(124, pc.NextChangeId);
    var pair = Assert.Single(pc.Markets);
    Assert.Equal("exalted|chaos", pair.MarketId);
    Assert.Equal("Metadata/Items/Currency/CurrencyRerollRare", pair.MarketPair[1]);
    Assert.Equal(100, pair.VolumeTraded[pair.MarketPair[1]]);
    Assert.Equal(20, pair.HighestStock[pair.MarketPair[1]]);
    Assert.Equal("https://web.poecdn.com/api/currency-exchange/123", handler.Requests[0].Url);
    Assert.Equal("https://web.poecdn.com/api/currency-exchange/xbox/456", handler.Requests[1].Url);
    Assert.DoesNotContain(handler.Requests, request => request.Url.Contains("oauth"));
    Assert.All(handler.Requests, request =>
    {
      Assert.Null(request.Authorization);
      Assert.Equal("Poe2scout/1.0.0 (contact: b@girardet.co.nz)", request.UserAgent);
    });
  }

  [Fact]
  public async Task RejectsMissingMarketPairDictionaryKeys()
  {
    var handler = new QueueHandler([
      _ => Json(HttpStatusCode.OK, SnapshotJson.Replace(
        """
            "Metadata/Items/Currency/CurrencyRerollRare": 20
        """,
        """
            "Metadata/Items/Currency/Unrelated": 20
        """))
    ]);
    var client = CreateClient(handler);

    await Assert.ThrowsAsync<System.Text.Json.JsonException>(
      () => client.GetSnapshot("pc", 123, CancellationToken.None));
  }

  [Theory]
  [InlineData(HttpStatusCode.TooManyRequests)]
  [InlineData(HttpStatusCode.BadRequest)]
  [InlineData(HttpStatusCode.InternalServerError)]
  public async Task DoesNotRetryOtherFailureStatuses(HttpStatusCode statusCode)
  {
    var handler = new QueueHandler([
      _ => new HttpResponseMessage(statusCode)
    ]);
    var client = CreateClient(handler);

    var exception = await Assert.ThrowsAsync<PoeApiException>(
      () => client.GetSnapshot("pc", 123, CancellationToken.None));

    Assert.Equal(statusCode, exception.StatusCode);
  }

  private static PoeCurrencyExchangeClient CreateClient(QueueHandler handler)
    => new(new HttpClient(handler), (_, _) => Task.CompletedTask);

  private static HttpResponseMessage Json(HttpStatusCode statusCode, string json)
    => new(statusCode) { Content = new StringContent(json, Encoding.UTF8, "application/json") };

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
