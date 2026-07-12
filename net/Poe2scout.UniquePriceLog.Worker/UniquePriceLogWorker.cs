using System.Globalization;
using System.Text.Json;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.Item;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.League.Models;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.PriceLog.Models;
using Poe2scout.Repositories.Service;
using Poe2scout.Repositories.UniqueItem;

namespace Poe2scout.UniquePriceLog.Worker;

public sealed class UniquePriceLogWorker(
  UniquePriceLogConfig config,
  IPoeTradeClient client,
  IServiceRepository serviceRepository,
  ILeagueRepository leagueRepository,
  IUniqueItemRepository uniqueItemRepository,
  ICurrencyItemRepository currencyItemRepository,
  IItemRepository itemRepository,
  IPriceLogRepository priceLogRepository,
  Func<TimeSpan, CancellationToken, Task>? delay = null) : BackgroundService
{
  private const int GameId = 2;
  private const int LeagueId = 23;
  private const int RealmId = 4;
  private const string Realm = "poe2";
  private const string BaseUrl = "https://www.pathofexile.com/api/trade2";

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
          await Delay(TimeSpan.FromSeconds(backoffSeconds), stoppingToken);
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
    var league = await leagueRepository.GetLeague(LeagueId);
    var baseUniqueItems = await uniqueItemRepository.GetCurrentUniqueItems(GameId);
    var baseCurrencyItems = await currencyItemRepository.GetAllCurrencyItems(GameId);
    var currentTime = DateTime.Now.ToString("HH", CultureInfo.InvariantCulture);
    var fetchedItemIds = await serviceRepository.GetFetchedItemIds(currentTime, league.LeagueId);
    var fetchedItemIdSet = fetchedItemIds.ToHashSet();
    var allItemIds = await itemRepository.GetAllItems(GameId);
    var itemIdsToFetch = allItemIds
      .Select(item => item.ItemId)
      .Where(itemId => !fetchedItemIdSet.Contains(itemId))
      .ToList();
    var uniqueItems = baseUniqueItems
      .Where(item => itemIdsToFetch.Contains(item.ItemId))
      .ToList();

    if (itemIdsToFetch.Count == 0)
    {
      await Delay(TimeSpan.FromMinutes(5), cancellationToken);
      return;
    }

    await ProcessUniques(uniqueItems, league, cancellationToken);

    foreach (var currencyItem in baseCurrencyItems)
    {
      if (currencyItem.ItemMetadata is null)
      {
        await SyncCurrencyMetadata(currencyItem, league, cancellationToken);
      }
    }

    await Delay(TimeSpan.FromMinutes(1), cancellationToken);
  }

  private async Task ProcessUniques(
    IReadOnlyList<UniqueItem> uniqueItems,
    League league,
    CancellationToken cancellationToken)
  {
    foreach (var uniqueItem in uniqueItems)
    {
      try
      {
        var prices = new[]
        {
          await FetchUnique(uniqueItem, league, "exalted", cancellationToken),
          await FetchUnique(uniqueItem, league, "chaos", cancellationToken),
          await FetchUnique(uniqueItem, league, "divine", cancellationToken)
        }
        .Where(price => price.Price > 0)
        .ToList();

        if (prices.Count == 0)
        {
          continue;
        }

        var lowestPrice = (double)long.MaxValue;
        var quantity = 0;
        foreach (var price in prices)
        {
          double itemPrice;
          if (price.Currency == league.BaseCurrencyApiId)
          {
            itemPrice = price.Price;
          }
          else
          {
            var currency = await currencyItemRepository.GetCurrencyItem(price.Currency, GameId)
                           ?? throw new InvalidOperationException($"Currency was not found: {price.Currency}");
            var currencyPrice = await priceLogRepository.GetItemPrice(
              currency.ItemId,
              league.LeagueId,
              RealmId,
              null);
            if (currencyPrice == 0)
            {
              continue;
            }

            itemPrice = price.Price * currencyPrice;
          }

          quantity += price.Quantity;
          if (itemPrice < lowestPrice)
          {
            lowestPrice = itemPrice;
          }
        }

        await RecordPrice(lowestPrice, uniqueItem.ItemId, league.LeagueId, quantity);
      }
      catch (UniqueItemDelistedException)
      {
        await uniqueItemRepository.SetUniqueItemCurrent(uniqueItem.UniqueItemId, false);
      }
    }
  }

  private async Task<PriceFetchResult> FetchUnique(
    UniqueItem uniqueItem,
    League league,
    string currency,
    CancellationToken cancellationToken)
  {
    var query = await client.SearchUniqueAsync(uniqueItem, league, currency, cancellationToken);
    if (query.Result.Count == 0)
    {
      return new PriceFetchResult(-1, 0, currency);
    }

    var itemIds = query.Result.Take(10).ToList();
    TradeFetchResponse fetchData;
    try
    {
      fetchData = await client.FetchAsync(itemIds, query.Id, cancellationToken);
    }
    catch (TradeClientException exception) when (exception.IsUnknownItemName)
    {
      throw new UniqueItemDelistedException(uniqueItem.UniqueItemId, uniqueItem.Name, exception);
    }

    if (fetchData.Result.All(result => result is not null))
    {
      var firstItem = fetchData.Result[0]?.Item
                      ?? throw new InvalidOperationException("Trade fetch result did not contain an item.");
      await SyncUniqueMetadata(firstItem, uniqueItem);
    }

    var prices = fetchData.Result
      .Where(result => result?.Listing?.Price is not null)
      .Select(result => ParseAmount(result!.Listing!.Price!.Amount))
      .Where(price => price is not null)
      .Select(price => price!.Value)
      .ToList();

    return prices.Count == 0
      ? new PriceFetchResult(-1, 0, currency)
      : new PriceFetchResult(prices[0], query.Total, currency);
  }

  private async Task SyncUniqueMetadata(JsonElement item, UniqueItem uniqueItem)
  {
    var metadata = UniqueItemMetadataExtractor.Extract(item);
    if (uniqueItem.ItemMetadata is null)
    {
      await uniqueItemRepository.SetUniqueItemMetadata(metadata, uniqueItem.UniqueItemId);
    }

    if (uniqueItem.IconUrl is null)
    {
      await uniqueItemRepository.UpdateUniqueIconUrl(
        (metadata["icon"] as string) ?? string.Empty,
        uniqueItem.UniqueItemId);
    }
  }

  private async Task SyncCurrencyMetadata(
    CurrencyItem currencyItem,
    League league,
    CancellationToken cancellationToken)
  {
    TradeSearchResponse query;
    try
    {
      query = await client.SearchCurrencyAsync(currencyItem, league, cancellationToken);
    }
    catch (TradeClientException)
    {
      return;
    }

    if (query.Result.Count == 0)
    {
      return;
    }

    var itemIds = query.Result.Take(10).ToList();
    var fetchData = await client.FetchAsync(itemIds, query.Id, cancellationToken);
    var firstItem = fetchData.Result[0]?.Item
                    ?? throw new InvalidOperationException("Trade fetch result did not contain an item.");
    var metadata = CurrencyItemMetadataExtractor.Extract(firstItem);

    if (currencyItem.ItemMetadata is null)
    {
      await currencyItemRepository.SetCurrencyItemMetadata(metadata, currencyItem.CurrencyItemId);
    }

    if (currencyItem.IconUrl is null)
    {
      await currencyItemRepository.UpdateCurrencyIconUrl(
        (metadata["icon"] as string) ?? string.Empty,
        currencyItem.CurrencyItemId);
    }
  }

  private async Task RecordPrice(double price, int itemId, int leagueId, int quantity)
  {
    if (price <= 0)
    {
      return;
    }

    await priceLogRepository.RecordPrice(new RecordPriceModel(
      itemId,
      leagueId,
      price,
      quantity,
      RealmId));
  }

  private Task Delay(TimeSpan duration, CancellationToken cancellationToken)
    => delay is null ? Task.Delay(duration, cancellationToken) : delay(duration, cancellationToken);

  private static double? ParseAmount(JsonElement amount)
  {
    if (amount.ValueKind == JsonValueKind.Number && amount.TryGetDouble(out var number))
    {
      return number;
    }

    return amount.ValueKind == JsonValueKind.String
           && double.TryParse(
             amount.GetString(),
             NumberStyles.Float,
             CultureInfo.InvariantCulture,
             out var parsed)
      ? parsed
      : null;
  }
}
