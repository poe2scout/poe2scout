using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.CurrencyItem.Models;
using Poe2scout.Repositories.Game;
using Poe2scout.Repositories.Game.Models;
using Poe2scout.Repositories.Item;
using Poe2scout.Repositories.Item.Models;
using Poe2scout.Repositories.UniqueItem;
using Poe2scout.Repositories.UniqueItem.Models;

namespace Poe2scout.ItemSync.Worker;

public sealed class ItemSyncWorker(
  ItemSyncConfig config,
  IItemSyncClient client,
  IGameRepository gameRepository,
  IItemRepository itemRepository,
  IUniqueItemRepository uniqueItemRepository,
  ICurrencyItemRepository currencyItemRepository,
  Func<TimeSpan, CancellationToken, Task>? delay = null) : BackgroundService
{
  protected override async Task ExecuteAsync(CancellationToken stoppingToken)
  {
    while (!stoppingToken.IsCancellationRequested)
    {
      await RunIteration(stoppingToken);
    }
  }

  public async Task RunIteration(CancellationToken cancellationToken)
  {
    var games = await gameRepository.GetGames();

    foreach (var game in games)
    {
      cancellationToken.ThrowIfCancellationRequested();

      var items = await client.GetItemsAsync(game.GggApiTradeIdentifier, cancellationToken);
      var currencies = await client.GetCurrenciesAsync(game.GggApiTradeIdentifier, cancellationToken);

      await SyncItems(items.Result!, game, cancellationToken);
      await SyncCurrencies(currencies.Result!, game.GameId, cancellationToken);
    }

    await Delay(TimeSpan.FromDays(1), cancellationToken);
  }

  private async Task SyncItems(
    IReadOnlyList<ItemFeedCategory> categories,
    Game game,
    CancellationToken cancellationToken)
  {
    var allTypes = await itemRepository.GetAllItemTypes();
    var allBaseItems = await itemRepository.GetAllBaseItems(game.GameId);
    var allCategories = await itemRepository.GetAllItemCategories();
    var allUniqueItems = await uniqueItemRepository.GetAllUniqueItems(game.GameId);

    foreach (var category in categories)
    {
      cancellationToken.ThrowIfCancellationRequested();

      var existingCategory = allCategories.FirstOrDefault(item => item.ApiId == category.Id);
      int categoryId;
      if (existingCategory is null)
      {
        categoryId = await itemRepository.CreateItemCategory(
          new CreateItemCategoryModel(category.Id!, category.Label!));
        allCategories = await itemRepository.GetAllItemCategories();
      }
      else
      {
        categoryId = existingCategory.ItemCategoryId;
      }

      foreach (var itemEntry in category.Entries!)
      {
        cancellationToken.ThrowIfCancellationRequested();

        var existingType = allTypes.FirstOrDefault(item => item.Value == itemEntry.Type);
        int typeId;
        if (existingType is null)
        {
          typeId = await itemRepository.CreateItemType(
            new CreateItemTypeModel(itemEntry.Type!, categoryId));
          allTypes = await itemRepository.GetAllItemTypes();
        }
        else
        {
          typeId = existingType.ItemTypeId;
        }

        var existingBaseItem = allBaseItems.FirstOrDefault(item => item.ItemTypeId == typeId);
        int baseItemId;
        if (existingBaseItem is null)
        {
          baseItemId = await itemRepository.CreateBaseItem(
            new CreateBaseItemModel(game.GameId, typeId, null, null));
          allBaseItems = await itemRepository.GetAllBaseItems(game.GameId);
          await itemRepository.CreateItem(new CreateItemModel(baseItemId, "base"));
        }
        else
        {
          baseItemId = existingBaseItem.BaseItemId;
        }

        if (itemEntry.Name is null)
        {
          continue;
        }

        if (itemEntry.Text is null)
        {
          throw new InvalidOperationException("Unique item missing name / text");
        }

        var existingUniqueItem = allUniqueItems.FirstOrDefault(item => item.Name == itemEntry.Name);
        if (existingUniqueItem is null)
        {
          var itemId = await itemRepository.CreateItem(new CreateItemModel(baseItemId, "unique"));
          await uniqueItemRepository.CreateUniqueItem(
            new CreateUniqueItemModel(itemId, null, itemEntry.Text, itemEntry.Name));
          allUniqueItems = await uniqueItemRepository.GetAllUniqueItems(game.GameId);
        }
        else if (!existingUniqueItem.IsCurrent)
        {
          await uniqueItemRepository.SetUniqueItemCurrent(existingUniqueItem.UniqueItemId, true);
          allUniqueItems = allUniqueItems
            .Select(item => item.UniqueItemId == existingUniqueItem.UniqueItemId
              ? item with { IsCurrent = true }
              : item)
            .ToList();
        }
      }
    }
  }

  private async Task SyncCurrencies(
    IReadOnlyList<CurrencyFeedCategory> categories,
    int gameId,
    CancellationToken cancellationToken)
  {
    IReadOnlyList<CurrencyCategory> allCurrencyCategories = [];
    IReadOnlyList<ItemCategory> allItemCategories = [];
    IReadOnlyList<ItemType> allTypes = [];
    IReadOnlyList<BaseItem> allBaseItems = [];
    IReadOnlyList<Poe2scout.Models.CurrencyItem> allCurrencyItems = [];

    async Task RefreshLists()
    {
      allCurrencyCategories = await currencyItemRepository.GetAllCurrencyCategories();
      allItemCategories = await itemRepository.GetAllItemCategories();
      allTypes = await itemRepository.GetAllItemTypes();
      allBaseItems = await itemRepository.GetAllBaseItems(gameId);
      allCurrencyItems = await currencyItemRepository.GetAllCurrencyItems(gameId);
    }

    await RefreshLists();

    foreach (var category in categories)
    {
      cancellationToken.ThrowIfCancellationRequested();

      if (category.Label is null)
      {
        continue;
      }

      if (category.Entries is null || !category.Entries.Any(currency => currency.Text != string.Empty))
      {
        continue;
      }

      category.Id = category.Id!.ToLowerInvariant();
      var existingCategory = allCurrencyCategories.FirstOrDefault(item => item.ApiId == category.Id);
      int categoryId;
      if (existingCategory is null)
      {
        categoryId = await currencyItemRepository.CreateCurrencyCategory(
          new CreateCurrencyCategoryModel(category.Id, category.Label));
      }
      else
      {
        categoryId = existingCategory.CurrencyCategoryId;
      }

      await RefreshLists();

      foreach (var currency in category.Entries!)
      {
        cancellationToken.ThrowIfCancellationRequested();

        if (currency.Text == string.Empty)
        {
          continue;
        }

        var itemCurrencyCategoryId = allItemCategories
          .First(item => item.ApiId == "currency")
          .ItemCategoryId;
        var existingType = allTypes.FirstOrDefault(item => item.Value == currency.Id);
        int typeId;
        if (existingType is null)
        {
          typeId = await itemRepository.CreateItemType(
            new CreateItemTypeModel(currency.Id!, itemCurrencyCategoryId));
        }
        else
        {
          typeId = existingType.ItemTypeId;
        }

        await RefreshLists();

        var existingBaseItem = allBaseItems.FirstOrDefault(item => item.ItemTypeId == typeId);
        int baseItemId;
        if (existingBaseItem is null)
        {
          var itemMetadata = new Dictionary<string, object>
          {
            ["id"] = currency.Id!,
            ["text"] = currency.Text!
          };
          baseItemId = await itemRepository.CreateBaseItem(
            new CreateBaseItemModel(gameId, typeId, currency.Image, itemMetadata));
          await itemRepository.CreateItem(new CreateItemModel(baseItemId, "base"));
        }
        else
        {
          baseItemId = existingBaseItem.BaseItemId;
        }

        var existingCurrency = allCurrencyItems.FirstOrDefault(item => item.ApiId == currency.Id);
        if (existingCurrency is null)
        {
          var itemId = await itemRepository.CreateItem(new CreateItemModel(baseItemId, "currency"));
          var imageUrl = currency.Image is null
            ? null
            : $"https://web.poecdn.com/{currency.Image}";
          var createResult = await currencyItemRepository.CreateCurrencyItem(
            new CreateCurrencyItemModel(
              itemId,
              categoryId,
              currency.Id!,
              null,
              currency.Text!,
              imageUrl));
          if (!createResult.Ok)
          {
            throw new InvalidOperationException(
              $"Failed to create currency item {currency.Id}: {createResult.Error}");
          }
        }

        await RefreshLists();
      }
    }
  }

  private Task Delay(TimeSpan duration, CancellationToken cancellationToken)
    => delay is null ? Task.Delay(duration, cancellationToken) : delay(duration, cancellationToken);
}
