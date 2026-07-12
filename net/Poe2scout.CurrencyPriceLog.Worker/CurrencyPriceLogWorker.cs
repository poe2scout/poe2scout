using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.Game;
using Poe2scout.Repositories.Game.Models;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.League.Models;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.PriceLog.Models;
using Poe2scout.Repositories.Realm;
using Poe2scout.Repositories.Realm.Models;
using Poe2scout.Repositories.Service;

namespace Poe2scout.CurrencyPriceLog.Worker;

public sealed class CurrencyPriceLogWorker(
  CurrencyPriceLogConfig config,
  IPoeCurrencyExchangeClient client,
  IServiceRepository serviceRepository,
  IRealmRepository realmRepository,
  ILeagueRepository leagueRepository,
  ICurrencyItemRepository currencyItemRepository,
  IGameRepository gameRepository,
  IPriceLogRepository priceLogRepository) : BackgroundService
{
  private const string CacheKey = "PriceFetch_Currency";

  protected override async Task ExecuteAsync(CancellationToken stoppingToken)
  {
    var backoffSeconds = config.BackoffInitialSeconds;
    while (!stoppingToken.IsCancellationRequested)
    {
      try
      {
        await RunIteration(stoppingToken);
        backoffSeconds = config.BackoffInitialSeconds;
      }
      catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
      {
        return;
      }
      catch (Exception)
      {
        try
        {
          await Task.Delay(TimeSpan.FromSeconds(backoffSeconds), stoppingToken);
        }
        catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
        {
          return;
        }

        backoffSeconds = Math.Min(backoffSeconds * 2, config.BackoffMaxSeconds);
      }
    }
  }

  public async Task RunIteration(CancellationToken cancellationToken)
  {
    var lastFetch = await serviceRepository.GetServiceCacheValue(CacheKey)
                    ?? throw new InvalidOperationException($"Missing service cache value: {CacheKey}");
    var currentEpoch = lastFetch.Value + 60 * 60;
    var nowEpoch = (long)(DateTime.UtcNow - DateTime.UnixEpoch).TotalSeconds;
    var delaySeconds = Math.Max(currentEpoch + 61 * 60 - nowEpoch, 0);
    await Task.Delay(TimeSpan.FromSeconds(delaySeconds), cancellationToken);

    var realms = await realmRepository.GetRealms();
    await Task.WhenAll(realms.Select(realm => ProcessRealm(currentEpoch, realm, cancellationToken)));
    await serviceRepository.SetServiceCacheValue(CacheKey, currentEpoch);
  }

  private async Task ProcessRealm(
    int currentEpoch,
    Realm realm,
    CancellationToken cancellationToken)
  {
    var data = await client.GetSnapshot(realm.ApiId, currentEpoch, cancellationToken);
    if (data.NextChangeId == currentEpoch)
    {
      //TODO: Log fetched too early.
      return;
    }

    if (data.Markets.Count == 0)
    {
      //TODO: Log no markets warning
      return;
    }

    var leagues = await leagueRepository.GetLeagues(realm.GameId);
    var currencyItems = await currencyItemRepository.GetAllCurrencyItems(realm.GameId);
    var bridgeCurrencies = await gameRepository.GetBridgeCurrencies(realm.GameId);
    var itemIdLookup = new Dictionary<string, int>();
    foreach (var currencyItem in currencyItems)
    {
      itemIdLookup[currencyItem.ApiId] = currencyItem.ItemId;
    }

    foreach (var league in leagues)
    {
      if (await priceLogRepository.GetPricesChecked(currentEpoch, league.LeagueId, realm.RealmId))
      {
        //TODO: Log prices already checked info.
        continue;
      }

      var finalPrices = await BuildFinalPricesForLeague(
        data,
        league,
        bridgeCurrencies,
        realm.RealmId,
        currentEpoch);
      var priceLogs = finalPrices.Values
        .Where(value => itemIdLookup.ContainsKey(value.ItemId) && value.Value != 0)
        .Select(value => new RecordPriceModel(
          itemIdLookup[value.ItemId],
          league.LeagueId,
          value.Value,
          value.QuantityTraded,
          realm.RealmId))
        .ToList();

      if (priceLogs.Count > 0)
      {
        await priceLogRepository.RecordPriceBulk(priceLogs, currentEpoch);
      }
    }
  }

  private async Task<Dictionary<string, CurrencyPrice>> BuildFinalPricesForLeague(
    CurrencyExchangeResponse data,
    League league,
    IReadOnlyList<BridgeCurrency> bridgeCurrencies,
    int realmId,
    int epoch)
  {
    var observations = CurrencyPriceCalculator.GetLeagueObservations(data, league);
    if (observations.Count == 0)
    {
      return [];
    }

    var historicalBridgePrices = new Dictionary<string, double>();
    if (bridgeCurrencies.Count > 0)
    {
      var bridgePrices = await priceLogRepository.GetItemPricesBefore(
        bridgeCurrencies.Select(item => item.ItemId).ToList(),
        league.LeagueId,
        realmId,
        epoch);
      for (var index = 0; index < Math.Min(bridgeCurrencies.Count, bridgePrices.Count); index++)
      {
        if (bridgePrices[index].Price != 0)
        {
          historicalBridgePrices[bridgeCurrencies[index].ApiId] = bridgePrices[index].Price;
        }
      }
    }

    return CurrencyPriceCalculator.BuildFinalPricesFromObservations(
      observations,
      league,
      bridgeCurrencies,
      historicalBridgePrices);
  }
}
