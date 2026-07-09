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
