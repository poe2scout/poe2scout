using System.Collections.Concurrent;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.PriceLog.Models;
using Poe2scout.Repositories.UniqueItem;

namespace Poe2scout.Api;

public record CacheKey(
  string Category,
  int LeagueId,
  int RealmId,
  int GameId,
  string ReferenceCurrency,
  int DataPoints,
  int FrequencyHours);

public record CacheEntry<T>(List<T> Value, DateTime ExpiresUtc);

public class EconomyCache(
  ICurrencyItemRepository currencyItemRepository, 
  IUniqueItemRepository uniqueItemRepository,
  ILeagueRepository leagueRepository,
  IPriceLogRepository priceLogRepository)
{
  private readonly Random random = new();
  
  private readonly ConcurrentDictionary<CacheKey, CacheEntry<CurrencyItemExtended>> currencyCache = new();
  private readonly ConcurrentDictionary<CacheKey, CacheEntry<UniqueItemExtended>> uniqueCache = new();
  
  public async Task<List<CurrencyItemExtended>> GetCurrencyPage(
    int leagueId,
    int realmId,
    int gameId,
    string category,
    string referenceCurrency,
    int dataPoints,
    int frequencyHours,
    string? search)
  {
    List<CurrencyItemExtended> result;
    var cacheKey = new CacheKey(category, leagueId, realmId, gameId, referenceCurrency, dataPoints, frequencyHours); 
    var cacheEntry = currencyCache.GetValueOrDefault(cacheKey);

    if (cacheEntry is not null && cacheEntry.ExpiresUtc > DateTime.UtcNow)
    {
      result = cacheEntry.Value;
    }
    else
    {
      result = await FetchCurrencyPage(cacheKey);
    }

    if (!string.IsNullOrEmpty(search))
    {
      result = result.Where(i => i.Text == search).ToList();
    }

    return result;
  }

  public async Task<List<UniqueItemExtended>> GetUniquePage(
    int leagueId,
    int realmId,
    int gameId,
    string category,
    string referenceCurrency,
    int dataPoints,
    int frequencyHours,
    string? search)
  {
    List<UniqueItemExtended> result;
    var cacheKey = new CacheKey(category, leagueId, realmId, gameId, referenceCurrency, dataPoints, frequencyHours); 
    var cacheEntry = uniqueCache.GetValueOrDefault(cacheKey);

    if (cacheEntry is not null && cacheEntry.ExpiresUtc > DateTime.UtcNow)
    {
      result = cacheEntry.Value;
    }
    else
    {
      result = await FetchUniquePage(cacheKey);
      uniqueCache[cacheKey] = new CacheEntry<UniqueItemExtended>(
        result,
        DateTime.UtcNow.AddHours(1).AddMinutes(random.Next(0, 16)));
    }

    if (!string.IsNullOrEmpty(search))
    {
      result = result.Where(i => string.Equals(i.Name, search, StringComparison.OrdinalIgnoreCase)).ToList();
    }

    return result;
  }

  private async Task<List<UniqueItemExtended>> FetchUniquePage(CacheKey cacheKey)
  {
    var leagueItemsTask = leagueRepository.GetItemsInCurrentLeague(cacheKey.LeagueId, cacheKey.RealmId);
    var categoryItemsTask = uniqueItemRepository.GetUniqueItemsByCategory(cacheKey.Category);

    await Task.WhenAll(leagueItemsTask, categoryItemsTask);
    
    var leagueItems = await leagueItemsTask;
    var categoryItems = await categoryItemsTask;
    
    var itemsInCurrentLeague = new HashSet<int>(leagueItems);

    var uniqueItems = categoryItems.Where(c => itemsInCurrentLeague.Contains(c.ItemId)).ToList();
    var itemIds = uniqueItems.Select(i => i.ItemId).ToList();

    if (itemIds.Count == 0)
    {
      return [];
    }
    
    var timeUtc = DateTime.UtcNow;
    var priceLogs = await GetCategoryPriceLogs(
      itemIds,
      cacheKey.LeagueId,
      cacheKey.RealmId,
      cacheKey.DataPoints,
      cacheKey.FrequencyHours,
      timeUtc);

    var referenceCurrencyPrice = 1.0;
    if (!string.IsNullOrEmpty(cacheKey.ReferenceCurrency))
    {
      var referenceCurrencyItem = await currencyItemRepository.GetCurrencyItem(
        cacheKey.ReferenceCurrency,
        cacheKey.GameId);

      if (referenceCurrencyItem is null)
      {
        throw new InvalidOperationException("Reference currency does not exist.");
      }

      referenceCurrencyPrice = await priceLogRepository.GetItemPrice(
        referenceCurrencyItem.ItemId,
        cacheKey.LeagueId,
        cacheKey.RealmId,
        null);

      var referenceCurrencyLogs = (await GetCategoryPriceLogs(
        [referenceCurrencyItem.ItemId],
        cacheKey.LeagueId,
        cacheKey.RealmId,
        cacheKey.DataPoints,
        cacheKey.FrequencyHours,
        timeUtc))[referenceCurrencyItem.ItemId];

      priceLogs = ConvertPriceLogMatrixFromBase(priceLogs, referenceCurrencyLogs);
    }

    var prices = await priceLogRepository.GetItemPrices(itemIds, cacheKey.LeagueId, cacheKey.RealmId);
    var pricesLookup = prices.ToDictionary(price => price.ItemId);
    var convertedCurrentPrices = ConvertPricesFromBase(
      pricesLookup.ToDictionary(kvp => kvp.Key, kvp => kvp.Value.Price),
      referenceCurrencyPrice);

    return uniqueItems
      .Select(item =>
      {
        convertedCurrentPrices.TryGetValue(item.ItemId, out var currentPrice);
        pricesLookup.TryGetValue(item.ItemId, out var itemPrice);

        return new UniqueItemExtended(
          item.UniqueItemId,
          item.ItemId,
          item.IconUrl,
          item.Text,
          item.Name,
          item.CategoryApiId,
          item.ItemMetadata,
          item.Type,
          item.IsChanceable,
          item.IsCurrent,
          priceLogs[item.ItemId],
          currentPrice,
          itemPrice?.Quantity);
      })
      .OrderByDescending(item => item.CurrentPrice ?? 0)
      .ToList();
  }

  private async Task<List<CurrencyItemExtended>> FetchCurrencyPage(CacheKey cacheKey)
  {
    DateTime expirationTimeUtc;
    var leagueItemsTask = leagueRepository.GetItemsInCurrentLeague(cacheKey.LeagueId, cacheKey.RealmId);
    var categoryItemsTask = currencyItemRepository.GetCurrencyItemsByCategory(cacheKey.Category);

    await Task.WhenAll(leagueItemsTask, categoryItemsTask);
    
    var leagueItems = await leagueItemsTask;
    var categoryItems = await categoryItemsTask;
    
    var itemsInCurrentLeague = new HashSet<int>(leagueItems);

    var currencyItems = categoryItems.Where(c => itemsInCurrentLeague.Contains(c.ItemId)).ToList();
    
    var itemIds = currencyItems.Select(i => i.ItemId).ToList();

    if (itemIds.Count == 0)
    {
      var nextHourUtc = DateTime.UtcNow.AddHours(1);
      var nextHourExactUtc = new DateTime(nextHourUtc.Year, nextHourUtc.Month, nextHourUtc.Day, nextHourUtc.Hour, 0, 0, DateTimeKind.Utc);
      expirationTimeUtc = nextHourExactUtc + TimeSpan.FromMinutes(5 + random.NextSingle() * 5);
      currencyCache[cacheKey] = new CacheEntry<CurrencyItemExtended>(Value: [], ExpiresUtc: expirationTimeUtc);

      return [];
    }
    
    var timeUtc = DateTime.UtcNow;
    var priceLogs = await GetCategoryPriceLogs(
      itemIds,
      cacheKey.LeagueId,
      cacheKey.RealmId,
      cacheKey.DataPoints,
      cacheKey.FrequencyHours,
      timeUtc);

    var referenceCurrencyPrice = 1.0;
    if (!string.IsNullOrEmpty(cacheKey.ReferenceCurrency))
    {
      var referenceCurrencyItem = await currencyItemRepository.GetCurrencyItem(
        cacheKey.ReferenceCurrency,
        cacheKey.GameId);

      if (referenceCurrencyItem is null)
      {
        throw new InvalidOperationException("Reference currency does not exist.");
      }

      referenceCurrencyPrice = await priceLogRepository.GetItemPrice(
        referenceCurrencyItem.ItemId,
        cacheKey.LeagueId,
        cacheKey.RealmId,
        null);

      var referenceCurrencyLogs = (await GetCategoryPriceLogs(
        [referenceCurrencyItem.ItemId],
        cacheKey.LeagueId,
        cacheKey.RealmId,
        cacheKey.DataPoints,
        cacheKey.FrequencyHours,
        timeUtc))[referenceCurrencyItem.ItemId];

      priceLogs = ConvertPriceLogMatrixFromBase(priceLogs, referenceCurrencyLogs);
    }

    var prices = await priceLogRepository.GetItemPrices(itemIds, cacheKey.LeagueId, cacheKey.RealmId);
    var pricesLookup = prices.ToDictionary(price => price.ItemId);
    var convertedCurrentPrices = ConvertPricesFromBase(
      pricesLookup.ToDictionary(kvp => kvp.Key, kvp => kvp.Value.Price),
      referenceCurrencyPrice);

    var result = currencyItems
      .Select(item =>
      {
        convertedCurrentPrices.TryGetValue(item.ItemId, out var currentPrice);
        pricesLookup.TryGetValue(item.ItemId, out var itemPrice);

        return new CurrencyItemExtended(
          item.CurrencyItemId,
          item.ItemId,
          item.CurrencyCategoryId,
          item.ApiId,
          item.Text,
          item.CategoryApiId,
          item.IconUrl,
          item.ItemMetadata,
          priceLogs[item.ItemId],
          currentPrice,
          itemPrice?.Quantity);
      })
      .OrderByDescending(item => item.CurrentPrice ?? 0)
      .ToList();

    expirationTimeUtc = GetNextHourExpirationUtc();
    currencyCache[cacheKey] = new CacheEntry<CurrencyItemExtended>(result, expirationTimeUtc);

    return result;
  }

  private async Task<Dictionary<int, IReadOnlyList<PriceLogEntry?>>> GetCategoryPriceLogs(
    List<int> itemIds,
    int leagueId,
    int realmId,
    int dataPoints,
    int frequencyHours,
    DateTime timeUtc)
  {
    if (frequencyHours == 24)
    {
      var dailyStatDates = GetDailyStatDates(dataPoints, timeUtc);
      
      return BuildDailyStatPriceLogs(
        itemIds,
        dailyStatDates,
        await priceLogRepository.GetItemDailyStats(
          itemIds,
          leagueId,
          realmId,
          dailyStatDates));
    }

    var bucketStarts = GetPriceHistoryBucketStarts(dataPoints, frequencyHours, timeUtc);
    return await priceLogRepository.GetItemPriceBucketStats(
      itemIds,
      leagueId,
      realmId,
      bucketStarts,
      frequencyHours);
  }

  private static List<DateOnly> GetDailyStatDates(int dataPoints, DateTime timeUtc)
  {
    var currentDate = DateOnly.FromDateTime(timeUtc);

    var result = new List<DateOnly>();
    for (var i = 0; i < dataPoints; i++)
    {
      result.Add(currentDate.AddDays(-i));
    }

    return result;
  }

  private static List<DateTime> GetPriceHistoryBucketStarts(int dataPoints, int frequencyHours, DateTime timeUtc)
  {
    var currentBlock = new DateTime(
      timeUtc.Year,
      timeUtc.Month,
      timeUtc.Day,
      timeUtc.Hour / frequencyHours * frequencyHours,
      0,
      0,
      DateTimeKind.Utc);

    return Enumerable
      .Range(0, dataPoints)
      .Select(index => currentBlock.AddHours(index * -frequencyHours))
      .ToList();
  }

  private static Dictionary<int, IReadOnlyList<PriceLogEntry?>> BuildDailyStatPriceLogs(List<int> itemIds, List<DateOnly> dates,
    IEnumerable<ItemDailyStats> dailyStats)
  {
    var results = itemIds
      .Select(i => (i, (IReadOnlyList<PriceLogEntry?>)Enumerable.Repeat<PriceLogEntry?>(null, dates.Count).ToList()))
      .ToDictionary(kvp => kvp.i, kvp => kvp.Item2);

    var dateIndices = new Dictionary<DateOnly, List<int>>();
    for (var i = 0; i < dates.Count; i++)
    {
      if (!dateIndices.TryGetValue(dates[i], out var indices))
      {
        indices = [];
        dateIndices[dates[i]] = indices;
      }

      indices.Add(i);
    }

    foreach (var dailyStat in dailyStats)
    {
      if (!results.TryGetValue(dailyStat.ItemId, out var logs) || !dateIndices.TryGetValue(dailyStat.Day, out var indices))
      {
        continue;
      }

      var mutableLogs = (List<PriceLogEntry?>)logs;
      foreach (var index in indices)
      {
        mutableLogs[index] = new PriceLogEntry(
          dailyStat.AvgPrice,
          dailyStat.Day.ToDateTime(TimeOnly.MinValue),
          dailyStat.Volume);
      }
    }

    return results;
  }

  private static Dictionary<int, IReadOnlyList<PriceLogEntry?>> ConvertPriceLogMatrixFromBase(
    Dictionary<int, IReadOnlyList<PriceLogEntry?>> priceLogsByItemId,
    IReadOnlyList<PriceLogEntry?> referenceCurrencyLogs)
  {
    var convertedLogs = new Dictionary<int, IReadOnlyList<PriceLogEntry?>>();

    foreach (var (itemId, priceLogs) in priceLogsByItemId)
    {
      var convertedItemLogs = new List<PriceLogEntry?>();
      for (var i = 0; i < priceLogs.Count; i++)
      {
        var priceLog = priceLogs[i];
        var referenceLog = i < referenceCurrencyLogs.Count ? referenceCurrencyLogs[i] : null;

        if (priceLog is null || referenceLog is null || referenceLog.Price == 0)
        {
          convertedItemLogs.Add(null);
          continue;
        }

        convertedItemLogs.Add(new PriceLogEntry(
          priceLog.Price / referenceLog.Price,
          priceLog.Time,
          priceLog.Quantity));
      }

      convertedLogs[itemId] = convertedItemLogs;
    }

    return convertedLogs;
  }

  private static Dictionary<int, double> ConvertPricesFromBase(
    Dictionary<int, double> pricesByItemId,
    double referenceCurrencyPrice)
  {
    if (referenceCurrencyPrice == 0)
    {
      return pricesByItemId.ToDictionary(kvp => kvp.Key, _ => 0.0);
    }

    return pricesByItemId.ToDictionary(kvp => kvp.Key, kvp => kvp.Value / referenceCurrencyPrice);
  }

  private DateTime GetNextHourExpirationUtc()
  {
    var nextHourUtc = DateTime.UtcNow.AddHours(1);
    var nextHourExactUtc = new DateTime(
      nextHourUtc.Year,
      nextHourUtc.Month,
      nextHourUtc.Day,
      nextHourUtc.Hour,
      0,
      0,
      DateTimeKind.Utc);
    
    return nextHourExactUtc + TimeSpan.FromMinutes(5 + random.NextSingle() * 5);
  }
}
