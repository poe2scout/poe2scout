using Poe2scout.Repositories.Game.Models;
using Poe2scout.Repositories.League.Models;

namespace Poe2scout.CurrencyPriceLog.Worker;

public static class CurrencyPriceCalculator
{
  public static Dictionary<string, CurrencyPrice> BuildFinalPricesFromObservations(
    IReadOnlyList<PriceObservation> observations,
    League league,
    IReadOnlyList<BridgeCurrency> bridgeCurrencies,
    IReadOnlyDictionary<string, double> fallbackBridgePrices)
  {
    var observationsByTarget = new Dictionary<string, List<PriceObservation>>();
    foreach (var observation in observations)
    {
      if (!observationsByTarget.TryGetValue(observation.TargetItem, out var targetObservations))
      {
        targetObservations = [];
        observationsByTarget[observation.TargetItem] = targetObservations;
      }

      targetObservations.Add(observation);
    }

    var resolvedPrices = new Dictionary<string, CurrencyPrice>
    {
      [league.BaseCurrencyApiId] = new(
        league.BaseCurrencyApiId,
        1.0,
        Math.Max(GetTotalQuantity(observationsByTarget, league.BaseCurrencyApiId), 1))
    };
    var resolvedQuoteItems = new HashSet<string> { league.BaseCurrencyApiId };

    foreach (var bridgeItem in bridgeCurrencies)
    {
      var targetObservations = observationsByTarget.GetValueOrDefault(bridgeItem.ApiId) ?? [];
      double? bridgePrice = null;
      if (targetObservations.Any(observation => observation.BaseItem == league.BaseCurrencyApiId))
      {
        bridgePrice = AggregateTargetPrice(targetObservations, resolvedPrices, resolvedQuoteItems);
      }

      if (bridgePrice is null)
      {
        if (!fallbackBridgePrices.TryGetValue(bridgeItem.ApiId, out var fallbackPrice))
        {
          continue;
        }

        bridgePrice = fallbackPrice;
      }

      resolvedPrices[bridgeItem.ApiId] = new CurrencyPrice(
        bridgeItem.ApiId,
        bridgePrice.Value,
        GetTotalQuantity(observationsByTarget, bridgeItem.ApiId));
      resolvedQuoteItems.Add(bridgeItem.ApiId);
    }

    var bridgeApiIds = bridgeCurrencies.Select(item => item.ApiId).ToHashSet();
    foreach (var itemApiId in observationsByTarget.Keys.Order(StringComparer.Ordinal))
    {
      if (itemApiId == league.BaseCurrencyApiId || bridgeApiIds.Contains(itemApiId))
      {
        continue;
      }

      var itemPrice = AggregateTargetPrice(
        observationsByTarget[itemApiId],
        resolvedPrices,
        resolvedQuoteItems);
      if (itemPrice is null)
      {
        continue;
      }

      resolvedPrices[itemApiId] = new CurrencyPrice(
        itemApiId,
        itemPrice.Value,
        GetTotalQuantity(observationsByTarget, itemApiId));
    }

    return resolvedPrices;
  }

  public static List<PriceObservation> GetLeagueObservations(
    CurrencyExchangeResponse data,
    League league)
  {
    var observations = new List<PriceObservation>();
    foreach (var listing in data.Markets.Where(pair => pair.League == league.Value))
    {
      var items = listing.MarketId.Split('|');
      if (items.Length != 2)
      {
        throw new InvalidOperationException($"Invalid market id: {listing.MarketId}");
      }

      observations.AddRange(CreatePairObservations(listing, items[0], items[1]));
    }

    return observations;
  }

  public static List<PriceObservation> CreatePairObservations(
    TradingPair listing,
    string itemOne,
    string itemTwo)
  {
    var itemOneVolume = listing.VolumeTraded[itemOne];
    var itemTwoVolume = listing.VolumeTraded[itemTwo];
    if (itemOneVolume == 0 || itemTwoVolume == 0)
    {
      return [];
    }

    return
    [
      new PriceObservation(itemOne, itemTwo, (double)itemOneVolume / itemTwoVolume, itemTwoVolume),
      new PriceObservation(itemTwo, itemOne, (double)itemTwoVolume / itemOneVolume, itemOneVolume)
    ];
  }

  private static int GetTotalQuantity(
    IReadOnlyDictionary<string, List<PriceObservation>> observationsByTarget,
    string targetItem)
    => observationsByTarget.TryGetValue(targetItem, out var observations)
      ? observations.Sum(observation => observation.QuantityOfTargetItem)
      : 0;

  private static double? AggregateTargetPrice(
    IReadOnlyList<PriceObservation> observations,
    IReadOnlyDictionary<string, CurrencyPrice> resolvedPrices,
    IReadOnlySet<string> allowedBases)
  {
    var candidates = new List<PriceCandidate>();
    foreach (var observation in observations)
    {
      if (!allowedBases.Contains(observation.BaseItem) ||
          !resolvedPrices.TryGetValue(observation.BaseItem, out var basePrice))
      {
        continue;
      }

      candidates.Add(new PriceCandidate(
        observation.ValueOfTargetItemInBaseItems * basePrice.Value,
        observation.QuantityOfTargetItem));
    }

    return AggregateWeightedPrice(candidates);
  }

  private static double? AggregateWeightedPrice(IReadOnlyList<PriceCandidate> candidates)
  {
    var totalQuantity = candidates.Sum(candidate => candidate.Quantity);
    if (totalQuantity == 0)
    {
      return null;
    }

    return candidates.Sum(candidate => candidate.Value * candidate.Quantity) / totalQuantity;
  }
}
