using System.Net;
using System.Text;
using System.Text.Json;
using Poe2scout.Models;
using Poe2scout.Repositories.League.Models;
using Poe2scout.UniquePriceLog.Worker;

namespace Poe2scout.UniquePriceLog.Worker.Tests;

public class PoeTradeClientTests
{
  [Fact]
  public async Task BuildsNonJewelSearchWithCorruptedFilter()
  {
    var handler = new QueueHandler(_ => Json(HttpStatusCode.OK, "{\"id\":\"query\",\"result\":[\"one\"],\"total\":1}"));
    var client = CreateClient(handler);

    await client.SearchUniqueAsync(Item("body_armour"), League(), "chaos", CancellationToken.None);

    Assert.Contains("/api/trade2/search/poe2/Standard", handler.Requests[0].Url);
    Assert.Contains("\"corrupted\":{\"option\":\"false\"}", handler.Requests[0].Body);
    Assert.Equal("POST", handler.Requests[0].Method);
  }

  [Fact]
  public async Task OmitsCorruptedFilterForJewels()
  {
    var handler = new QueueHandler(_ => Json(HttpStatusCode.OK, "{\"id\":\"query\",\"result\":[],\"total\":0}"));
    var client = CreateClient(handler);

    await client.SearchUniqueAsync(Item("jewel"), League(), "chaos", CancellationToken.None);

    Assert.DoesNotContain("corrupted", handler.Requests[0].Body);
  }

  [Fact]
  public async Task FetchParsesTradePriceAndUsesExpectedQueryParameters()
  {
    var handler = new QueueHandler(_ => Json(
      HttpStatusCode.OK,
      "{\"result\":[{\"listing\":{\"price\":{\"amount\":\"3.5\"}},\"item\":{\"name\":\"Test\"}}]}"));
    var client = CreateClient(handler);

    var response = await client.FetchAsync(["one", "two"], "query id", CancellationToken.None);

    var result = Assert.Single(response.Result);
    Assert.Equal("3.5", result!.Listing!.Price!.Amount.GetString());
    Assert.Equal("GET", handler.Requests[0].Method);
    Assert.Contains("/fetch/", handler.Requests[0].Url);
    Assert.Contains("one", handler.Requests[0].Url);
    Assert.Contains("two", handler.Requests[0].Url);
    Assert.Contains("query=", handler.Requests[0].Url);
    Assert.Contains("realm=poe2", handler.Requests[0].Url);
  }

  [Fact]
  public async Task MapsUnknownItemNameToDelistedException()
  {
    var handler = new QueueHandler(_ => Json(HttpStatusCode.BadRequest, "Unknown item name"));
    var client = CreateClient(handler);

    var exception = await Assert.ThrowsAsync<UniqueItemDelistedException>(() =>
      client.SearchUniqueAsync(Item("body_armour"), League(), "chaos", CancellationToken.None));

    Assert.Equal(1, exception.UniqueItemId);
    Assert.Equal("Test Unique", exception.ItemName);
  }

  [Fact]
  public async Task DoesNotRetryRateLimitFailures()
  {
    var handler = new QueueHandler(_ => Json(HttpStatusCode.TooManyRequests, "rate limited"));
    var client = CreateClient(handler);

    var exception = await Assert.ThrowsAsync<TradeClientException>(() =>
      client.SearchCurrencyAsync(
        new CurrencyItem(1, 100, 1, "exalted", null, "Exalted Orb", "currency", null, null),
        League(),
        CancellationToken.None));

    Assert.Equal(HttpStatusCode.TooManyRequests, exception.StatusCode);
    Assert.Single(handler.Requests);
  }

  private static PoeTradeClient CreateClient(QueueHandler handler)
    => new(new HttpClient(handler), (_, _) => Task.CompletedTask);

  private static UniqueItem Item(string category)
    => new(1, 101, null, "Test", "Test Unique", category, null, "Armour", null, true);

  private static League League()
    => new(23, "Standard", "Standard", 100, "exalted", null, "Exalted Orb", null, true);

  private static HttpResponseMessage Json(HttpStatusCode statusCode, string json)
    => new(statusCode)
    {
      Content = new StringContent(json, Encoding.UTF8, "application/json")
    };

  private sealed class QueueHandler(Func<HttpRequestMessage, HttpResponseMessage> responseFactory)
    : HttpMessageHandler
  {
    public List<RecordedRequest> Requests { get; } = [];

    protected override async Task<HttpResponseMessage> SendAsync(
      HttpRequestMessage request,
      CancellationToken cancellationToken)
    {
      Requests.Add(new RecordedRequest(
        request.Method.Method,
        request.RequestUri?.ToString() ?? string.Empty,
        request.Content is null ? string.Empty : await request.Content.ReadAsStringAsync(cancellationToken)));
      return responseFactory(request);
    }
  }

  private sealed record RecordedRequest(string Method, string Url, string Body);
}
