using System.Diagnostics;
using Poe2scout.Repositories.Game.Models;
using Poe2scout.Repositories.League.Models;

namespace Poe2scout.CurrencyPriceLog.Worker.Tests;

public class CurrencyPriceCalculatorTests
{
  [Fact]
  public void ResolvesBridgesInRankOrderAndUsesEarlierBridgeQuotes()
  {
    var prices = Build(
      [Observation("exalted", "chaos", .1, 100), Observation("exalted", "divine", 40, 1), Observation("chaos", "divine", 300, 1)],
      [Bridge("chaos", 1), Bridge("divine", 2)]);

    Assert.Equal(.1, prices["chaos"].Value, 12);
    Assert.Equal(35, prices["divine"].Value, 12);
  }

  [Fact]
  public void SupportsBridgeInsertedBetweenExistingRanks()
  {
    var prices = Build(
      [
        Observation("exalted", "chaos", .1, 100),
        Observation("exalted", "annul", 1.5, 10),
        Observation("chaos", "annul", 15, 10),
        Observation("exalted", "divine", 32, 1),
        Observation("chaos", "divine", 320, 1),
        Observation("annul", "divine", 20, 1)
      ],
      [Bridge("chaos", 1), Bridge("annul", 2), Bridge("divine", 3)]);

    Assert.Equal(1.5, prices["annul"].Value, 12);
    Assert.Equal(31.333333333333332, prices["divine"].Value, 12);
  }

  [Fact]
  public void NonBridgeUsesAllResolvedBridgeQuotesAndAllQuantities()
  {
    var prices = Build(
      [
        Observation("exalted", "chaos", .1, 100),
        Observation("exalted", "divine", 30, 1),
        Observation("chaos", "divine", 300, 1),
        Observation("exalted", "mirror", 10, 4),
        Observation("chaos", "mirror", 100, 5),
        Observation("divine", "mirror", 1.0 / 3, 6)
      ],
      [Bridge("chaos", 1), Bridge("divine", 2)]);

    Assert.Equal(10, prices["mirror"].Value, 12);
    Assert.Equal(15, prices["mirror"].QuantityTraded);
  }

  [Fact]
  public void UnresolvedQuoteRequiresBridgeConfiguration()
  {
    var observations = new[]
    {
      Observation("exalted", "chaos", .1, 100),
      Observation("mirror", "soulcore", 2, 7)
    };
    var withoutMirror = Build(observations, [Bridge("chaos", 1)]);
    var withMirror = Build(
      [.. observations, Observation("exalted", "mirror", 50, 1)],
      [Bridge("chaos", 1), Bridge("mirror", 2)]);

    Assert.DoesNotContain("soulcore", withoutMirror);
    Assert.Equal(100, withMirror["soulcore"].Value, 12);
  }

  [Fact]
  public void BridgeFallsBackToHistoricalPrice()
  {
    var prices = Build(
      [Observation("exalted", "chaos", .1, 100), Observation("chaos", "divine", 300, 1), Observation("divine", "mirror", 1, 2)],
      [Bridge("chaos", 1), Bridge("divine", 2)],
      new Dictionary<string, double> { ["divine"] = 28 });

    Assert.Equal(28, prices["divine"].Value, 12);
    Assert.Equal(28, prices["mirror"].Value, 12);
  }

  [Fact]
  public void UnresolvedBridgeWithoutFallbackIsExcludedDownstream()
  {
    var prices = Build(
      [Observation("exalted", "chaos", .1, 100), Observation("chaos", "divine", 300, 1), Observation("divine", "mirror", 1, 2)],
      [Bridge("chaos", 1), Bridge("divine", 2)]);

    Assert.DoesNotContain("divine", prices);
    Assert.DoesNotContain("mirror", prices);
  }

  [Fact]
  public void QuantityIncludesUnpriceablePairs()
  {
    var prices = Build(
      [
        Observation("exalted", "chaos", .1, 100), Observation("exalted", "divine", 30, 1),
        Observation("chaos", "divine", 300, 1), Observation("exalted", "relic", 10, 4),
        Observation("chaos", "relic", 100, 5), Observation("divine", "relic", 1.0 / 3, 6),
        Observation("mirror", "relic", .2, 7)
      ],
      [Bridge("chaos", 1), Bridge("divine", 2)]);

    Assert.Equal(10, prices["relic"].Value, 12);
    Assert.Equal(22, prices["relic"].QuantityTraded);
  }

  [Fact]
  public void RouteFlipDoesNotCollapseQuantityOrCauseSinglePairJump()
  {
    var common = new[]
    {
      Observation("exalted", "chaos", .1, 100), Observation("exalted", "divine", 30, 1),
      Observation("chaos", "divine", 300, 1), Observation("chaos", "artifact", 100, 100),
      Observation("divine", "artifact", 1.0 / 3, 100)
    };
    var bridges = new[] { Bridge("chaos", 1), Bridge("divine", 2) };
    var first = Build([.. common, Observation("exalted", "artifact", 20, 1)], bridges);
    var second = Build([.. common, Observation("exalted", "artifact", .5, 1)], bridges);

    Assert.Equal(201, first["artifact"].QuantityTraded);
    Assert.Equal(201, second["artifact"].QuantityTraded);
    Assert.True(Math.Abs(first["artifact"].Value - second["artifact"].Value) < .2);
  }

  [Fact]
  public void CreatesBidirectionalObservationsAndDropsZeroVolumePairs()
  {
    var pair = Pair("exalted|chaos", new() { ["exalted"] = 10, ["chaos"] = 100 });
    var observations = CurrencyPriceCalculator.CreatePairObservations(pair, "exalted", "chaos");

    Assert.Collection(
      observations,
      value => Assert.Equal(new PriceObservation("exalted", "chaos", .1, 100), value),
      value => Assert.Equal(new PriceObservation("chaos", "exalted", 10, 10), value));
    Assert.Empty(CurrencyPriceCalculator.CreatePairObservations(
      Pair("exalted|chaos", new() { ["exalted"] = 0, ["chaos"] = 100 }),
      "exalted",
      "chaos"));
  }

  [Fact]
  public void AggregationRemainsLinearForLargeSnapshot()
  {
    var observations = new List<PriceObservation>
    {
      Observation("exalted", "chaos", .1, 1000), Observation("exalted", "annul", 1.5, 100),
      Observation("chaos", "annul", 15, 100), Observation("exalted", "divine", 30, 50),
      Observation("chaos", "divine", 300, 50), Observation("annul", "divine", 20, 50)
    };
    for (var index = 0; index < 4000; index++)
    {
      var item = $"item-{index}";
      observations.AddRange([
        Observation("exalted", item, 10 + index % 5, 4), Observation("chaos", item, 100 + index % 5 * 10, 5),
        Observation("divine", item, (10 + index % 3) / 30.0, 6), Observation("mirror", item, .5, 7)
      ]);
    }

    var stopwatch = Stopwatch.StartNew();
    var prices = Build(observations, [Bridge("chaos", 1), Bridge("annul", 2), Bridge("divine", 3)]);

    Assert.True(stopwatch.Elapsed < TimeSpan.FromSeconds(2), $"Aggregation took {stopwatch.Elapsed}.");
    Assert.Equal(4004, prices.Count);
  }

  internal static League League() => new(1, "Test League", "Test", 100, "exalted", "Exalted Orb", null, true);
  internal static BridgeCurrency Bridge(string apiId, int rank) => new(rank, rank, apiId, apiId, null, rank);
  internal static PriceObservation Observation(string baseItem, string targetItem, double price, int quantity)
    => new(baseItem, targetItem, price, quantity);
  internal static TradingPair Pair(string marketId, Dictionary<string, int> volumes, string league = "Test League")
    => new(league, marketId, volumes, []);

  private static Dictionary<string, CurrencyPrice> Build(
    IReadOnlyList<PriceObservation> observations,
    IReadOnlyList<BridgeCurrency> bridges,
    IReadOnlyDictionary<string, double>? fallback = null)
    => CurrencyPriceCalculator.BuildFinalPricesFromObservations(
      observations,
      League(),
      bridges,
      fallback ?? new Dictionary<string, double>());
}
