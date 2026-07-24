using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyExchange;
using Poe2scout.Repositories.CurrencyExchange.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.PriceLog.Models;
using Poe2scout.Repositories.Realm.Models;
using Poe2scout.Repositories.Realm;
using Poe2scout.Repositories.Service;

namespace Poe2scout.CurrencyExchange.Worker;

public sealed class CurrencyExchangeWorker(
  ICurrencyExchangeClient client,
  IServiceRepository serviceRepository,
  IRealmRepository realmRepository,
  ILeagueRepository leagueRepository,
  ICurrencyItemRepository currencyItemRepository,
  IPriceLogRepository priceLogRepository,
  ICurrencyExchangeRepository currencyExchangeRepository,
  CurrencyExchangeDiagnostics diagnostics,
  Func<TimeSpan, CancellationToken, Task>? delay = null) : BackgroundService
{
  private const string ExchangeCacheKey = "CurrencyExchange";
  private const string PriceFetchCacheKey = "PriceFetch_Currency";
  private static readonly TimeSpan PriceFetchWait = TimeSpan.FromMinutes(10);

  protected override async Task ExecuteAsync(CancellationToken stoppingToken)
  {

    while (!stoppingToken.IsCancellationRequested)
    {
      try
      {
        await RunIteration(stoppingToken);
      }
      catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
      {
        return;
      }
      catch (Exception ex)
      {
        diagnostics.RecordException(ex);

        throw;
      }
    }
  }

  public async Task RunIteration(CancellationToken cancellationToken)
  {
    var lastExchange = await serviceRepository.GetServiceCacheValue(ExchangeCacheKey)
                       ?? throw new InvalidOperationException(
                         $"Missing service cache value: {ExchangeCacheKey}");
    var lastPriceFetch = await serviceRepository.GetServiceCacheValue(PriceFetchCacheKey)
                         ?? throw new InvalidOperationException(
                           $"Missing service cache value: {PriceFetchCacheKey}");

    if (lastPriceFetch.Value <= lastExchange.Value)
    {
      await Delay(PriceFetchWait, cancellationToken);
      return;
    }

    var timeToFetch = lastExchange.Value + 60 * 60;
    var currentEpoch = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
    var delaySeconds = Math.Max(timeToFetch + 60 * 5 - currentEpoch, 0);
    await Delay(TimeSpan.FromSeconds(delaySeconds), cancellationToken);

    var realms = await realmRepository.GetRealms();
    var nextChangeIds = await Task.WhenAll(
      realms.Select(realm => ProcessRealmSnapshot(
        realm,
        timeToFetch,
        cancellationToken)));

    if (nextChangeIds.Any(nextChangeId => nextChangeId is null))
    {
      return;
    }

    var nextChangeId = nextChangeIds[0]
                       ?? throw new InvalidOperationException("No realm snapshot was returned.");
    await serviceRepository.SetServiceCacheValue(
      ExchangeCacheKey,
      nextChangeId - 60 * 60);
    await currencyExchangeRepository.UpdatePairHistories();
  }

  private async Task<int?> ProcessRealmSnapshot(
    Realm realm,
    int? timeToFetch,
    CancellationToken cancellationToken)
  {
    var data = await client.GetSnapshot(realm.ApiId, timeToFetch, cancellationToken);
    var targetEpoch = data.NextChangeId - 60 * 60;
    var targetTime = DateTimeOffset.FromUnixTimeSeconds(targetEpoch).LocalDateTime;

    if (!await serviceRepository.GetCurrencyFetchStatus(targetTime))
    {
      await Delay(PriceFetchWait, cancellationToken);
      return null;
    }

    var leagues = await leagueRepository.GetLeagues(realm.GameId);

    var existingSnapshotLeagueIds = (await currencyExchangeRepository.GetExistingSnapshotLeagueIds(
      targetEpoch,
      realm.RealmId)).ToHashSet();
    leagues = leagues
      .Where(league => !existingSnapshotLeagueIds.Contains(league.LeagueId))
      .ToList();

    if (leagues.Count == 0)
    {
      return data.NextChangeId;
    }

    var currencyLookup = (await currencyItemRepository.GetAllCurrencyItemsWithBaseId(realm.GameId))
      .ToDictionary(x => x.BaseItemTypeId, x => x);

    var unknownBaseIds = data.Markets
      .SelectMany(market => market.MarketPair)
      .Where(baseId => !currencyLookup.ContainsKey(baseId))
      .Distinct(StringComparer.Ordinal)
      .ToList();

    if (unknownBaseIds.Count != 0)
    {
      diagnostics.RecordUnknownBaseIds(targetEpoch, realm.RealmId, unknownBaseIds);
    }
    
    var leaguePrices = new Dictionary<int, IReadOnlyList<ItemPriceInRange>>();
    var currencyItemIds = currencyLookup.Values.Select(currency => currency.ItemId).ToList();

    foreach (var league in leagues)
    {
      leaguePrices[league.LeagueId] = await priceLogRepository.GetItemPricesInRange(
        currencyItemIds,
        league.LeagueId,
        realm.RealmId,
        targetTime,
        DateTimeOffset.FromUnixTimeSeconds(data.NextChangeId).LocalDateTime);
    }

    foreach (var league in leagues)
    {
      var prices = leaguePrices[league.LeagueId];
      if (prices.All(price => price.Price == 0))
      {
        continue;
      }

      var priceLookup = prices.ToDictionary(price => price.ItemId);
      var snapshotPairs = new List<CurrencyExchangeSnapshotPair>();
      foreach (var pair in data.Markets.Where(pair => pair.League == league.Value))
      {
        if (!currencyLookup.TryGetValue(pair.MarketPair[0], out var currencyOne)
            || !currencyLookup.TryGetValue(pair.MarketPair[1], out var currencyTwo))
        {
          continue;
        }

        var currencyOneData = GetPairData(
          currencyOne,
          priceLookup,
          pair,
          currencyTwo);
        var currencyTwoData = GetPairData(
          currencyTwo,
          priceLookup,
          pair,
          currencyOne);
        var mostLiquidData = priceLookup[currencyOne.ItemId].Quantity
          > priceLookup[currencyTwo.ItemId].Quantity
            ? currencyOneData
            : currencyTwoData;

        snapshotPairs.Add(new CurrencyExchangeSnapshotPair(
          currencyOne.ItemId,
          currencyTwo.ItemId,
          mostLiquidData.ValueTraded,
          currencyOneData,
          currencyTwoData));
      }

      var volume = snapshotPairs.Sum(pair => pair.Volume);
      var marketCap = snapshotPairs.Sum(pair =>
        pair.CurrencyOneData.StockValue + pair.CurrencyTwoData.StockValue);

      if (volume == 0 && marketCap == 0)
      {
        continue;
      }

      await currencyExchangeRepository.CreateSnapshot(new CurrencyExchangeSnapshot(
        targetEpoch,
        league.LeagueId,
        realm.RealmId,
        snapshotPairs,
        volume,
        marketCap));
    }

    return data.NextChangeId;
  }

  private static CurrencyExchangeSnapshotPairData GetPairData(
    CurrencyItemWithBaseId currency,
    Dictionary<int, ItemPriceInRange> priceLookup,
    TradingPair pair,
    CurrencyItemWithBaseId otherCurrency)
  {
    var currencyPrice = priceLookup[currency.ItemId];
    var volumeTraded = pair.VolumeTraded[currency.BaseItemTypeId];
    var valueTraded = volumeTraded * currencyPrice.Price;
    var relativePrice = volumeTraded == 0
      ? 0
      : (double)pair.VolumeTraded[otherCurrency.BaseItemTypeId] / volumeTraded
        * priceLookup[otherCurrency.ItemId].Price;
    var highestStock = pair.HighestStock[currency.BaseItemTypeId];

    return new CurrencyExchangeSnapshotPairData(
      (decimal)valueTraded,
      (decimal)relativePrice,
      volumeTraded,
      highestStock,
      (decimal)(highestStock * currencyPrice.Price));
  }

  private Task Delay(TimeSpan duration, CancellationToken cancellationToken)
    => delay is null ? Task.Delay(duration, cancellationToken) : delay(duration, cancellationToken);
}
