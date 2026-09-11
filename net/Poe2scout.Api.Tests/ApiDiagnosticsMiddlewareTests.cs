using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.AspNetCore.Routing.Patterns;
using Microsoft.Extensions.Logging;
using Xunit;

namespace Poe2scout.Api.Tests;

public sealed class ApiDiagnosticsMiddlewareTests
{
  [Fact]
  public async Task MiddlewareUsesTheRouteTemplateInsteadOfResolvedRouteValues()
  {
    using var harness = new ApiDiagnosticsTests.DiagnosticsHarness();
    var context = CreateContext(
      "/Standard/Leagues/Settlers/Items/1234",
      "/{realm}/Leagues/{leagueName}/Items/{itemId:int}");
    var middleware = new ApiDiagnosticsMiddleware(
      nextContext =>
      {
        nextContext.Response.StatusCode = StatusCodes.Status200OK;
        return Task.CompletedTask;
      },
      harness.Diagnostics);

    await middleware.InvokeAsync(context);

    var measurement = Assert.Single(harness.LongMeasurements);
    Assert.Equal("/{realm}/Leagues/{leagueName}/Items/{itemId:int}", measurement.Tags["http.route"]);
    Assert.DoesNotContain("Standard", measurement.Tags.Values);
    Assert.DoesNotContain("Settlers", measurement.Tags.Values);
    Assert.DoesNotContain("1234", measurement.Tags.Values);
  }

  [Fact]
  public async Task MiddlewareRecordsAndRethrowsUnhandledExceptions()
  {
    using var harness = new ApiDiagnosticsTests.DiagnosticsHarness();
    var context = CreateContext("/Realms", "/Realms");
    var expected = new InvalidOperationException("boom");
    var middleware = new ApiDiagnosticsMiddleware(_ => throw expected, harness.Diagnostics);

    var actual = await Assert.ThrowsAsync<InvalidOperationException>(() => middleware.InvokeAsync(context));

    Assert.Same(expected, actual);
    Assert.Equal("server_error", Assert.Single(harness.LongMeasurements).Tags["request.outcome"]);
    var log = Assert.Single(harness.Logger.Entries);
    Assert.Equal(LogLevel.Error, log.Level);
    Assert.Same(expected, log.Exception);
  }

  [Fact]
  public async Task MiddlewareTreatsClientCancellationLikeAnyOtherUnhandledException()
  {
    using var harness = new ApiDiagnosticsTests.DiagnosticsHarness();
    using var cancellation = new CancellationTokenSource();
    cancellation.Cancel();
    var context = CreateContext("/Realms", "/Realms");
    context.RequestAborted = cancellation.Token;
    var expected = new OperationCanceledException(cancellation.Token);
    var middleware = new ApiDiagnosticsMiddleware(_ => throw expected, harness.Diagnostics);

    var actual = await Assert.ThrowsAsync<OperationCanceledException>(() => middleware.InvokeAsync(context));

    Assert.Same(expected, actual);
    Assert.Equal("server_error", Assert.Single(harness.LongMeasurements).Tags["request.outcome"]);
    var log = Assert.Single(harness.Logger.Entries);
    Assert.Equal(LogLevel.Error, log.Level);
    Assert.Same(expected, log.Exception);
  }

  [Theory]
  [InlineData(false, false)]
  [InlineData(true, false)]
  [InlineData(false, true)]
  public async Task MiddlewareExcludesUnmatchedMetadataOptOutAndOptionsRequests(
    bool useOptOutMetadata,
    bool useOptionsMethod)
  {
    using var harness = new ApiDiagnosticsTests.DiagnosticsHarness();
    var context = useOptOutMetadata || useOptionsMethod
      ? CreateContext("/health/live", "/health/live", useOptOutMetadata)
      : new DefaultHttpContext();
    context.Request.Method = useOptionsMethod ? HttpMethods.Options : HttpMethods.Get;
    var middleware = new ApiDiagnosticsMiddleware(_ => Task.CompletedTask, harness.Diagnostics);

    await middleware.InvokeAsync(context);

    Assert.Empty(harness.LongMeasurements);
    Assert.Empty(harness.DoubleMeasurements);
    Assert.Empty(harness.Logger.Entries);
  }

  [Theory]
  [InlineData("/random-bot-url", null, "GET", 404, false)]
  [InlineData("/health/live", "/health/live", "GET", 200, true)]
  [InlineData("/openapi/v1.json", "/openapi/{documentName}.json", "GET", 200, true)]
  [InlineData("/Realms", "/Realms", "OPTIONS", 204, false)]
  [InlineData("/random-bot-url", null, "CUSTOM-BOT-METHOD", 405, false)]
  public async Task AllRequestsIncludesTrafficExcludedFromProductMetrics(
    string path, string? template, string method, int status, bool excluded)
  {
    using var harness = new ApiDiagnosticsTests.DiagnosticsHarness();
    var context = template is null ? new DefaultHttpContext() : CreateContext(path, template, excluded);
    context.Request.Path = path;
    context.Request.Method = method;
    var product = new ApiDiagnosticsMiddleware(ctx =>
    {
      ctx.Response.StatusCode = status;
      return Task.CompletedTask;
    }, harness.Diagnostics);
    var all = new AllRequestsDiagnosticsMiddleware(product.InvokeAsync, harness.Diagnostics);

    await all.InvokeAsync(context);

    var count = Assert.Single(harness.LongMeasurements);
    Assert.Equal(ApiDiagnostics.AllRequestCountInstrumentName, count.InstrumentName);
    Assert.Equal(1, count.Value);
    Assert.Equal(template ?? "unmatched", count.Tags["http.route"]);
    Assert.Equal(method == "CUSTOM-BOT-METHOD" ? "_OTHER" : method, count.Tags["http.request.method"]);
    Assert.Equal(status, count.Tags["http.response.status_code"]);
    Assert.Equal(3, count.Tags.Count);
    Assert.Empty(harness.DoubleMeasurements);
  }

  [Theory]
  [InlineData(false)]
  [InlineData(true)]
  public async Task AllRequestsAndProductRequestsEachCountOnce(bool throws)
  {
    using var harness = new ApiDiagnosticsTests.DiagnosticsHarness();
    var context = CreateContext("/Standard/Leagues/Settlers/Items/1234", "/{realm}/Leagues/{league}/Items/{id:int}");
    var expected = new InvalidOperationException("boom");
    var product = new ApiDiagnosticsMiddleware(_ => throws ? throw expected : Task.CompletedTask, harness.Diagnostics);
    var all = new AllRequestsDiagnosticsMiddleware(product.InvokeAsync, harness.Diagnostics);

    if (throws)
      Assert.Same(expected, await Assert.ThrowsAsync<InvalidOperationException>(() => all.InvokeAsync(context)));
    else
      await all.InvokeAsync(context);

    Assert.Equal(2, harness.LongMeasurements.Count);
    var count = Assert.Single(harness.LongMeasurements.Where(m => m.InstrumentName == ApiDiagnostics.AllRequestCountInstrumentName));
    Assert.Single(harness.LongMeasurements.Where(m => m.InstrumentName == ApiDiagnostics.RequestCountInstrumentName));
    Assert.Equal(1, count.Value);
    Assert.Equal(throws ? 500 : 200, count.Tags["http.response.status_code"]);
    Assert.Equal("/{realm}/Leagues/{league}/Items/{id:int}", count.Tags["http.route"]);
  }

  [Fact]
  public async Task AllRequestsCountsCorsPreflightBeforeCorsShortCircuits()
  {
    using var harness = new ApiDiagnosticsTests.DiagnosticsHarness();
    var services = new ServiceCollection();
    services.AddLogging();
    services.AddCors(options => options.AddDefaultPolicy(policy => policy
      .WithOrigins("https://poe2scout.com").AllowAnyMethod().AllowAnyHeader()));
    using var provider = services.BuildServiceProvider();
    var app = new ApplicationBuilder(provider);
    app.Use(next => new AllRequestsDiagnosticsMiddleware(next, harness.Diagnostics).InvokeAsync);
    app.UseCors();
    var reachedEndpoint = false;
    app.Run(_ => { reachedEndpoint = true; return Task.CompletedTask; });
    var context = new DefaultHttpContext { RequestServices = provider };
    context.Request.Method = "OPTIONS";
    context.Request.Headers.Origin = "https://poe2scout.com";
    context.Request.Headers.AccessControlRequestMethod = "GET";

    await app.Build()(context);

    Assert.False(reachedEndpoint);
    var count = Assert.Single(harness.LongMeasurements);
    Assert.Equal(ApiDiagnostics.AllRequestCountInstrumentName, count.InstrumentName);
    Assert.Equal(204, count.Tags["http.response.status_code"]);
    Assert.Equal("OPTIONS", count.Tags["http.request.method"]);
  }

  private static DefaultHttpContext CreateContext(string path, string routeTemplate, bool excluded = false)
  {
    var metadata = excluded
      ? new EndpointMetadataCollection(ExcludeFromApiDiagnosticsMetadata.Instance)
      : EndpointMetadataCollection.Empty;
    var endpoint = new RouteEndpoint(
      _ => Task.CompletedTask,
      RoutePatternFactory.Parse(routeTemplate),
      0,
      metadata,
      routeTemplate);
    var context = new DefaultHttpContext();
    context.Request.Method = HttpMethods.Get;
    context.Request.Path = path;
    context.SetEndpoint(endpoint);
    return context;
  }
}
