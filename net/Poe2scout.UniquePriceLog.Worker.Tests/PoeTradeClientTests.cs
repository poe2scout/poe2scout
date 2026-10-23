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
    var responses = 0;
    var handler = new QueueHandler(_ => ++responses == 1
      ? RateLimited(3600, content)
      : SearchSuccess());
    var client = new PoeTradeClient(new HttpClient(handler), (duration, _) =>
    {
      delays.Add(duration);
      if (duration == TimeSpan.FromSeconds(3602))
      {
        Assert.Single(handler.Requests);
        Assert.False(content.Disposed);
      }
      return Task.CompletedTask;
    });

    await client.SearchUniqueAsync(Item("jewel"), League(), "chaos", CancellationToken.None);

    Assert.Equal(new[] { TimeSpan.FromSeconds(3602), TimeSpan.FromSeconds(4) }, delays);
    Assert.Equal(2, handler.Requests.Count);
    Assert.Equal(handler.Requests[0], handler.Requests[1]);
    Assert.True(content.Disposed);
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
    Assert.Equal(6, delays.FindAll(duration => duration == TimeSpan.FromSeconds(62)).Count);
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
      if (duration == TimeSpan.FromSeconds(62))
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

    Assert.Equal(new[] { TimeSpan.FromSeconds(62), TimeSpan.FromSeconds(4) }, delays);
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
      if (duration == TimeSpan.FromSeconds(62))
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

  [Fact]
  public async Task UsesStrictestWindowAcrossAllRulesAndRefreshesAfterEachResponse()
  {
    var delays = new List<TimeSpan>();
    var responses = 0;
    var handler = new QueueHandler(_ => ++responses == 1
      ? WithRateLimits(SearchSuccess(), "ip, account", "12:4:600, 16:12:600", "8:10:600, 4:30:600")
      : WithRateLimits(SearchSuccess(), ip: "4:3:600"));
    var client = new PoeTradeClient(new HttpClient(handler), (duration, _) =>
    {
      // Every delay follows its corresponding HTTP request, including the first.
      Assert.Equal(delays.Count + 1, handler.Requests.Count);
      delays.Add(duration);
      return Task.CompletedTask;
    });

    await client.SearchUniqueAsync(Item("jewel"), League(), "chaos", CancellationToken.None);
    await client.SearchUniqueAsync(Item("jewel"), League(), "divine", CancellationToken.None);

    Assert.Equal(new[] { TimeSpan.FromSeconds(9.5), TimeSpan.FromSeconds(2.75) }, delays);
  }

  [Fact]
  public async Task RateLimitIntervalCanExceedRetryAfter()
  {
    var delays = new List<TimeSpan>();
    var responses = 0;
    var handler = new QueueHandler(_ => ++responses == 1
      ? WithRateLimits(RateLimited(1), ip: "1:10:300") : SearchSuccess());
    var client = new PoeTradeClient(new HttpClient(handler), (duration, _) =>
    {
      delays.Add(duration);
      return Task.CompletedTask;
    });

    await client.SearchUniqueAsync(Item("jewel"), League(), "chaos", CancellationToken.None);

    Assert.Equal(new[] { TimeSpan.FromSeconds(12), TimeSpan.FromSeconds(4) }, delays);
  }

  [Theory]
  [InlineData(403, 30, 60, 300)]
  [InlineData(405, 30, 60, 300)]
  [InlineData(503, 1, 600, 602)]
  public async Task RetryBackoffAndRateLimitUseOneCombinedWait(int status, int hits, int window, int expectedSeconds)
  {
    var delays = new List<TimeSpan>();
    var content = new TrackingContent();
    var responses = 0;
    var handler = new QueueHandler(_ => ++responses == 1
      ? WithRateLimits(new HttpResponseMessage((HttpStatusCode)status) { Content = content }, ip: $"{hits}:{window}:300")
      : SearchSuccess());
    var client = new PoeTradeClient(new HttpClient(handler), (duration, _) =>
    {
      Assert.Equal(delays.Count > 0, content.Disposed);
      delays.Add(duration);
      return Task.CompletedTask;
    });

    await client.SearchUniqueAsync(Item("jewel"), League(), "chaos", CancellationToken.None);

    Assert.Equal(new[] { TimeSpan.FromSeconds(expectedSeconds), TimeSpan.FromSeconds(4) }, delays);
  }

  [Fact]
  public async Task RetryExhaustionStillDelaysBeforeThrowing()
  {
    var delays = new List<TimeSpan>();
    var handler = new QueueHandler(_ => Json(HttpStatusCode.ServiceUnavailable, "unavailable"));
    var client = new PoeTradeClient(new HttpClient(handler), (duration, _) =>
    {
      delays.Add(duration);
      return Task.CompletedTask;
    });

    await Assert.ThrowsAsync<TradeClientException>(() =>
      client.SearchUniqueAsync(Item("jewel"), League(), "chaos", CancellationToken.None));

    Assert.Equal(5, handler.Requests.Count);
    Assert.Equal(new[] { TimeSpan.FromSeconds(300), TimeSpan.FromSeconds(300),
      TimeSpan.FromSeconds(300), TimeSpan.FromSeconds(300), TimeSpan.FromSeconds(4) }, delays);
  }

  [Fact]
  public async Task ClientErrorIsDisposedAndDelayedBeforeThrowing()
  {
    var content = new TrackingContent();
    var handler = new QueueHandler(_ => WithRateLimits(
      new HttpResponseMessage(HttpStatusCode.BadRequest) { Content = content }));
    var waited = false;
    var client = new PoeTradeClient(new HttpClient(handler), (duration, _) =>
    {
      Assert.False(content.Disposed);
      Assert.Equal(TimeSpan.FromSeconds(4), duration);
      waited = true;
      return Task.CompletedTask;
    });

    await Assert.ThrowsAsync<TradeClientException>(() =>
      client.SearchUniqueAsync(Item("jewel"), League(), "chaos", CancellationToken.None));

    Assert.True(waited);
    Assert.True(content.Disposed);
  }

  [Fact]
  public async Task CancellationDisposesSuccessfulResponseWhileWaiting()
  {
    var waiting = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
    using var cancellation = new CancellationTokenSource();
    var content = new TrackingContent();
    var handler = new QueueHandler(_ => WithRateLimits(
      new HttpResponseMessage(HttpStatusCode.OK) { Content = content }));
    var client = new PoeTradeClient(new HttpClient(handler), async (_, token) =>
    {
      waiting.SetResult();
      await Task.Delay(Timeout.InfiniteTimeSpan, token);
    });

    var search = client.SearchUniqueAsync(Item("jewel"), League(), "chaos", cancellation.Token);
    await waiting.Task.WaitAsync(TimeSpan.FromSeconds(5));
    Assert.False(search.IsCompleted);
    Assert.False(content.Disposed);
    cancellation.Cancel();

    await Assert.ThrowsAnyAsync<OperationCanceledException>(() => search.WaitAsync(TimeSpan.FromSeconds(5)));
    Assert.True(content.Disposed);
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
    return WithRateLimits(response);
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
    => WithRateLimits(new HttpResponseMessage(statusCode)
    {
      Content = new StringContent(json, Encoding.UTF8, "application/json")
    });

  private static HttpResponseMessage WithRateLimits(
    HttpResponseMessage response,
    string rules = "ip",
    string ip = "30:60:300",
    string? account = null)
  {
    response.Headers.Remove("X-Rate-Limit-Policy");
    response.Headers.Remove("X-Rate-Limit-Rules");
    response.Headers.Remove("X-Rate-Limit-Ip");
    response.Headers.TryAddWithoutValidation("X-Rate-Limit-Policy", "trade-test");
    response.Headers.TryAddWithoutValidation("X-Rate-Limit-Rules", rules);
    response.Headers.TryAddWithoutValidation("X-Rate-Limit-Ip", ip);
    if (account is not null)
    {
      response.Headers.TryAddWithoutValidation("X-Rate-Limit-Account", account);
    }
    return response;
  }

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
