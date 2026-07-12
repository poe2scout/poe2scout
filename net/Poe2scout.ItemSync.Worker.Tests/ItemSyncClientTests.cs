using System.Net;
using System.Text;
using System.Text.Json;
using Poe2scout.ItemSync.Worker;

namespace Poe2scout.ItemSync.Worker.Tests;

public class ItemSyncClientTests
{
  [Fact]
  public async Task FetchesItemsWithExpectedUrlAndUserAgent()
  {
    var handler = new RecordingHandler(_ => Json(HttpStatusCode.OK, """
      {"RESULT":[{"ID":"body_armour","LABEL":"Body Armour","ENTRIES":[{"TYPE":"Armour","NAME":"Test","TEXT":"Description","FLAGS":{"foo":true}}]}]}
      """));
    var client = new ItemSyncClient(new HttpClient(handler));

    var response = await client.GetItemsAsync("poe2", CancellationToken.None);

    Assert.Equal("body_armour", Assert.Single(response.Result!).Id);
    Assert.Equal("Test", Assert.Single(response.Result?[0].Entries!).Name);
    Assert.Equal("https://www.pathofexile.com/api/poe2/data/items", handler.Requests[0].Url);
    Assert.Equal("POE2SCOUT (contact: b@girardet.co.nz)", handler.Requests[0].UserAgent);
  }

  [Fact]
  public async Task FetchesCurrenciesWithExpectedUrl()
  {
    var handler = new RecordingHandler(_ => Json(HttpStatusCode.OK, """
      {"result":[{"id":"Currency","label":"Currency","entries":[{"id":"exalted","text":"Exalted Orb","image":"items/exalted.png"}]}]}
      """));
    var client = new ItemSyncClient(new HttpClient(handler));

    var response = await client.GetCurrenciesAsync("poe2", CancellationToken.None);

    Assert.Equal("exalted", Assert.Single(Assert.Single(response.Result!).Entries!).Id);
    Assert.Equal("https://www.pathofexile.com/api/poe2/data/static", handler.Requests[0].Url);
  }

  [Fact]
  public async Task ThrowsForNonSuccessResponses()
  {
    var handler = new RecordingHandler(_ => Json(HttpStatusCode.ServiceUnavailable, "unavailable"));
    var client = new ItemSyncClient(new HttpClient(handler));

    await Assert.ThrowsAsync<HttpRequestException>(() =>
      client.GetItemsAsync("poe2", CancellationToken.None));
  }

  [Fact]
  public async Task ThrowsForInvalidPayloads()
  {
    var handler = new RecordingHandler(_ => Json(HttpStatusCode.OK, "{}"));
    var client = new ItemSyncClient(new HttpClient(handler));

    await Assert.ThrowsAsync<JsonException>(() =>
      client.GetItemsAsync("poe2", CancellationToken.None));
  }

  private static HttpResponseMessage Json(HttpStatusCode statusCode, string json)
    => new(statusCode)
    {
      Content = new StringContent(json, Encoding.UTF8, "application/json")
    };

  private sealed class RecordingHandler(Func<HttpRequestMessage, HttpResponseMessage> responseFactory)
    : HttpMessageHandler
  {
    public List<RecordedRequest> Requests { get; } = [];

    protected override Task<HttpResponseMessage> SendAsync(
      HttpRequestMessage request,
      CancellationToken cancellationToken)
    {
      Requests.Add(new RecordedRequest(
        request.RequestUri?.ToString() ?? string.Empty,
        request.Headers.UserAgent.ToString()));
      return Task.FromResult(responseFactory(request));
    }
  }

  private sealed record RecordedRequest(string Url, string UserAgent);
}
