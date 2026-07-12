using System.Diagnostics.Metrics;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing.Patterns;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Poe2scout;
using Xunit;

namespace Poe2scout.Api.Tests;

public sealed class ApiDiagnosticsTests
{
  [Fact]
  public void SlowRequestThresholdCanBeOverriddenThroughRootConfiguration()
  {
    var configuration = new ConfigurationBuilder()
      .AddInMemoryCollection(new Dictionary<string, string?>
      {
        ["SlowRequestThresholdMs"] = "1250"
      })
      .Build();

    var config = BaseConfig.FromConfig<ApiConfig>(configuration);

    Assert.Equal(1250, config.SlowRequestThresholdMs);
  }

  [Theory]
  [InlineData(200, ApiRequestOutcome.Success)]
  [InlineData(302, ApiRequestOutcome.Success)]
  [InlineData(400, ApiRequestOutcome.ClientError)]
  [InlineData(404, ApiRequestOutcome.ClientError)]
  [InlineData(500, ApiRequestOutcome.ServerError)]
  [InlineData(503, ApiRequestOutcome.ServerError)]
  public void ClassifyOutcomeUsesServiceFailureSemantics(int statusCode, ApiRequestOutcome expected)
  {
    Assert.Equal(expected, ApiDiagnostics.ClassifyOutcome(statusCode));
  }

  [Fact]
  public void RecordRequestEmitsOnlyTheTwoCustomInstrumentsWithBoundedTags()
  {
    using var harness = new DiagnosticsHarness();
    const string route = "/{realm}/Leagues/{leagueName}/Items/{itemId:int}";

    harness.Diagnostics.RecordRequest(
      route,
      HttpMethods.Get,
      StatusCodes.Status200OK,
      ApiRequestOutcome.Success,
      TimeSpan.FromMilliseconds(125),
      "/Standard/Leagues/Settlers/Items/1234");

    var count = Assert.Single(harness.LongMeasurements);
    Assert.Equal(ApiDiagnostics.RequestCountInstrumentName, count.InstrumentName);
    Assert.Equal(1, count.Value);
    Assert.Equal(route, count.Tags["http.route"]);
    Assert.Equal(HttpMethods.Get, count.Tags["http.request.method"]);
    Assert.Equal(StatusCodes.Status200OK, count.Tags["http.response.status_code"]);
    Assert.Equal("success", count.Tags["request.outcome"]);

    var duration = Assert.Single(harness.DoubleMeasurements);
    Assert.Equal(ApiDiagnostics.RequestDurationInstrumentName, duration.InstrumentName);
    Assert.Equal(0.125, duration.Value, 3);
    Assert.Equal(route, duration.Tags["http.route"]);
    Assert.Equal(HttpMethods.Get, duration.Tags["http.request.method"]);
    Assert.Equal("success", duration.Tags["request.outcome"]);
    Assert.DoesNotContain("http.response.status_code", duration.Tags.Keys);

    Assert.DoesNotContain(
      harness.AllTagValues,
      value => value.Contains("Settlers", StringComparison.Ordinal) ||
               value.Contains("1234", StringComparison.Ordinal));
    Assert.Empty(harness.Logger.Entries);
  }

  [Fact]
  public void FastClientErrorIsMeasuredWithoutBeingLogged()
  {
    using var harness = new DiagnosticsHarness();

    harness.Diagnostics.RecordRequest(
      "/Realms/{realm}/Filters",
      HttpMethods.Get,
      StatusCodes.Status400BadRequest,
      ApiRequestOutcome.ClientError,
      TimeSpan.FromMilliseconds(20),
      "/Realms/Invalid/Filters");

    Assert.Equal("client_error", Assert.Single(harness.LongMeasurements).Tags["request.outcome"]);
    Assert.Empty(harness.Logger.Entries);
  }

  [Fact]
  public void SlowRequestEmitsOneWarning()
  {
    using var harness = new DiagnosticsHarness();

    harness.Diagnostics.RecordRequest(
      "/{realm}/Leagues/{leagueName}/Items",
      HttpMethods.Get,
      StatusCodes.Status200OK,
      ApiRequestOutcome.Success,
      TimeSpan.FromMilliseconds(800),
      "/Standard/Leagues/Settlers/Items");

    var entry = Assert.Single(harness.Logger.Entries);
    Assert.Equal(LogLevel.Warning, entry.Level);
    Assert.Equal("ApiRequestSlow", entry.EventId.Name);
    Assert.Equal("/{realm}/Leagues/{leagueName}/Items", entry.Properties["HttpRoute"]);
    Assert.Equal(800, entry.Properties["DurationMs"]);
    Assert.DoesNotContain("TraceId", entry.Properties.Keys);
  }

  [Fact]
  public void SlowServerErrorEmitsOneErrorWithException()
  {
    using var harness = new DiagnosticsHarness();
    var exception = new InvalidOperationException("Database unavailable");

    harness.Diagnostics.RecordRequest(
      "/{realm}/Leagues",
      HttpMethods.Get,
      StatusCodes.Status500InternalServerError,
      ApiRequestOutcome.ServerError,
      TimeSpan.FromSeconds(2),
      "/Standard/Leagues",
      exception);

    var entry = Assert.Single(harness.Logger.Entries);
    Assert.Equal(LogLevel.Error, entry.Level);
    Assert.Equal("ApiRequestFailed", entry.EventId.Name);
    Assert.Same(exception, entry.Exception);
  }

  internal sealed class DiagnosticsHarness : IDisposable
  {
    private readonly TestMeterFactory meterFactory = new();
    private readonly MeterListener listener = new();

    public DiagnosticsHarness()
    {
      listener.InstrumentPublished = (instrument, meterListener) =>
      {
        if (instrument.Meter.Name == ApiDiagnostics.MeterName)
        {
          meterListener.EnableMeasurementEvents(instrument);
        }
      };
      listener.SetMeasurementEventCallback<long>((instrument, value, tags, _) =>
        LongMeasurements.Add(new LongMeasurement(instrument.Name, value, CopyTags(tags))));
      listener.SetMeasurementEventCallback<double>((instrument, value, tags, _) =>
        DoubleMeasurements.Add(new DoubleMeasurement(instrument.Name, value, CopyTags(tags))));
      listener.Start();

      Logger = new ListLogger<ApiDiagnostics>();
      Diagnostics = new ApiDiagnostics(meterFactory, Logger, new ApiConfig());
    }

    public ApiDiagnostics Diagnostics { get; }
    public ListLogger<ApiDiagnostics> Logger { get; }
    public List<LongMeasurement> LongMeasurements { get; } = [];
    public List<DoubleMeasurement> DoubleMeasurements { get; } = [];

    public IEnumerable<string> AllTagValues =>
      LongMeasurements.SelectMany(measurement => measurement.Tags.Values)
        .Concat(DoubleMeasurements.SelectMany(measurement => measurement.Tags.Values))
        .Select(value => value?.ToString() ?? string.Empty);

    public void Dispose()
    {
      listener.Dispose();
      meterFactory.Dispose();
    }

    private static Dictionary<string, object?> CopyTags(ReadOnlySpan<KeyValuePair<string, object?>> tags)
    {
      var result = new Dictionary<string, object?>(StringComparer.Ordinal);
      foreach (var tag in tags)
      {
        result[tag.Key] = tag.Value;
      }

      return result;
    }
  }

  internal sealed record LongMeasurement(string InstrumentName, long Value, Dictionary<string, object?> Tags);
  internal sealed record DoubleMeasurement(string InstrumentName, double Value, Dictionary<string, object?> Tags);

  internal sealed class TestMeterFactory : IMeterFactory
  {
    private readonly Meter meter = new(ApiDiagnostics.MeterName);

    public Meter Create(MeterOptions options)
    {
      return meter;
    }

    public void Dispose()
    {
      meter.Dispose();
    }
  }

  internal sealed class ListLogger<T> : ILogger<T>
  {
    public List<LogEntry> Entries { get; } = [];

    public IDisposable? BeginScope<TState>(TState state) where TState : notnull
    {
      return null;
    }

    public bool IsEnabled(LogLevel logLevel)
    {
      return true;
    }

    public void Log<TState>(
      LogLevel logLevel,
      EventId eventId,
      TState state,
      Exception? exception,
      Func<TState, Exception?, string> formatter)
    {
      var properties = state is IEnumerable<KeyValuePair<string, object?>> values
        ? values.ToDictionary(value => value.Key, value => value.Value, StringComparer.Ordinal)
        : new Dictionary<string, object?>(StringComparer.Ordinal);
      Entries.Add(new LogEntry(logLevel, eventId, formatter(state, exception), exception, properties));
    }
  }

  internal sealed record LogEntry(
    LogLevel Level,
    EventId EventId,
    string Message,
    Exception? Exception,
    Dictionary<string, object?> Properties);
}
