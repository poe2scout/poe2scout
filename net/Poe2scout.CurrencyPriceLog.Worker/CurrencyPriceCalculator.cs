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
    var baseCurrencyId = league.BaseCurrencyBaseItemTypeId
                         ?? throw new InvalidOperationException(
                           $"League {league.Value} base currency is missing a base item type ID.");
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
      [baseCurrencyId] = new(
        baseCurrencyId,
        1.0,
        Math.Max(GetTotalQuantity(observationsByTarget, baseCurrencyId), 1))
    };
    var resolvedQuoteItems = new HashSet<string> { baseCurrencyId };

    foreach (var bridgeItem in bridgeCurrencies)
    {
      var bridgeId = bridgeItem.BaseItemTypeId
                     ?? throw new InvalidOperationException(
                       $"Bridge currency {bridgeItem.Text} is missing a base item type ID.");
      var targetObservations = observationsByTarget.GetValueOrDefault(bridgeId) ?? [];
      double? bridgePrice = null;
      if (targetObservations.Any(observation => observation.BaseItem == baseCurrencyId))
      {
        bridgePrice = AggregateTargetPrice(targetObservations, resolvedPrices, resolvedQuoteItems);
      }

      if (bridgePrice is null)
      {
        if (!fallbackBridgePrices.TryGetValue(bridgeId, out var fallbackPrice))
        {
          continue;
        }

        bridgePrice = fallbackPrice;
      }

      resolvedPrices[bridgeId] = new CurrencyPrice(
        bridgeId,
        bridgePrice.Value,
        GetTotalQuantity(observationsByTarget, bridgeId));
      resolvedQuoteItems.Add(bridgeId);
    }

    var bridgeBaseIds = bridgeCurrencies
      .Select(item => item.BaseItemTypeId
                      ?? throw new InvalidOperationException(
                        $"Bridge currency {item.Text} is missing a base item type ID."))
      .ToHashSet();
    foreach (var itemBaseId in observationsByTarget.Keys.Order(StringComparer.Ordinal))
    {
      if (itemBaseId == baseCurrencyId || bridgeBaseIds.Contains(itemBaseId))
      {
        continue;
      }

      var itemPrice = AggregateTargetPrice(
        observationsByTarget[itemBaseId],
        resolvedPrices,
        resolvedQuoteItems);
      if (itemPrice is null)
      {
        continue;
      }

      resolvedPrices[itemBaseId] = new CurrencyPrice(
        itemBaseId,
        itemPrice.Value,
        GetTotalQuantity(observationsByTarget, itemBaseId));
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

      observations.AddRange(CreatePairObservations(
        listing,
        listing.MarketPair[0],
        listing.MarketPair[1]));
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
