using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Poe2scout.Models;
using Poe2scout.Repositories.League.Models;
using Xunit;

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
  public async Task WaitsRetryAfterSecondsAndRetriesSameRequest()
  {
    var delays = new List<TimeSpan>();
    var content = new TrackingContent();
    var handler = new QueueHandler(_ => delays.Count == 1
      ? RateLimited(3600, content)
      : SearchSuccess());
    var client = new PoeTradeClient(new HttpClient(handler), (duration, _) =>
    {
      delays.Add(duration);
      if (duration == TimeSpan.FromHours(1))
      {
        Assert.Single(handler.Requests);
        Assert.True(content.Disposed);
      }
      return Task.CompletedTask;
    });

    await client.SearchUniqueAsync(Item("jewel"), League(), "chaos", CancellationToken.None);

    Assert.Equal(new[] { TimeSpan.FromSeconds(17), TimeSpan.FromHours(1), TimeSpan.FromSeconds(17) }, delays);
    Assert.Equal(2, handler.Requests.Count);
    Assert.Equal(handler.Requests[0], handler.Requests[1]);
  }

  [Fact]
  public async Task RepeatedRateLimitsDoNotExhaustRetryLimit()
  {
    var delays = new List<TimeSpan>();
    var responses = 0;
    var handler = new QueueHandler(_ => ++responses <= 6 ? RateLimited(60) : SearchSuccess());
    var client = new PoeTradeClient(new HttpClient(handler), (duration, _) =>
    {
      delays.Add(duration);
      return Task.CompletedTask;
    });

    await client.SearchUniqueAsync(Item("jewel"), League(), "chaos", CancellationToken.None);

    Assert.Equal(7, handler.Requests.Count);
    Assert.Equal(6, delays.FindAll(duration => duration == TimeSpan.FromSeconds(60)).Count);
  }

  [Theory]
  [InlineData(true)]
  [InlineData(false)]
  public async Task FetchesAndCurrencySearchesHonorRetryAfter(bool fetch)
  {
    var delays = new List<TimeSpan>();
    var responses = 0;
    var handler = new QueueHandler(_ => ++responses == 1
      ? RateLimited(60)
      : fetch ? Json(HttpStatusCode.OK, "{\"result\":[]}") : SearchSuccess());
    var client = new PoeTradeClient(new HttpClient(handler), (duration, _) =>
    {
      if (duration == TimeSpan.FromSeconds(60))
      {
        Assert.Single(handler.Requests);
      }
      delays.Add(duration);
      return Task.CompletedTask;
    });

    if (fetch)
    {
      await client.FetchAsync(["one"], "query", CancellationToken.None);
    }
    else
    {
      await client.SearchCurrencyAsync(
        new CurrencyItem(1, 100, 1, "exalted", null, "Exalted Orb", "currency", null, null),
        League(), CancellationToken.None);
    }

    var spacing = TimeSpan.FromSeconds(fetch ? 3 : 17);
    Assert.Equal(new[] { spacing, TimeSpan.FromSeconds(60), spacing }, delays);
    Assert.Equal(2, handler.Requests.Count);
  }

  [Fact]
  public async Task CancellationInterruptsCooldownWithoutAnotherRequest()
  {
    var waiting = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
    using var cancellation = new CancellationTokenSource();
    var handler = new QueueHandler(_ => RateLimited(60));
    var client = new PoeTradeClient(new HttpClient(handler), async (duration, token) =>
    {
      if (duration == TimeSpan.FromSeconds(60))
      {
        waiting.SetResult();
        await Task.Delay(Timeout.InfiniteTimeSpan, token);
      }
    });

    var search = client.SearchUniqueAsync(Item("jewel"), League(), "chaos", cancellation.Token);
    await waiting.Task.WaitAsync(TimeSpan.FromSeconds(5));
    cancellation.Cancel();

    await Assert.ThrowsAnyAsync<OperationCanceledException>(() => search.WaitAsync(TimeSpan.FromSeconds(5)));
    Assert.Single(handler.Requests);
  }

  private static HttpResponseMessage SearchSuccess()
    => Json(HttpStatusCode.OK, "{\"id\":\"query\",\"result\":[],\"total\":0}");

  private static HttpResponseMessage RateLimited(int seconds, HttpContent? content = null)
  {
    var response = new HttpResponseMessage(HttpStatusCode.TooManyRequests)
    {
      Content = content ?? new StringContent("rate limited")
    };
    response.Headers.RetryAfter = new RetryConditionHeaderValue(TimeSpan.FromSeconds(seconds));
    return response;
  }

  private sealed class TrackingContent() : StringContent("rate limited")
  {
    public bool Disposed { get; private set; }
    protected override void Dispose(bool disposing)
    {
      Disposed = true;
      base.Dispose(disposing);
    }
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
