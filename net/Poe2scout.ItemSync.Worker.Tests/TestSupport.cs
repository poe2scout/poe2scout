using Microsoft.Extensions.Configuration;
using Moq;
using Poe2scout;
using Poe2scout.ItemSync.Worker;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.CurrencyItem.Models;
using Poe2scout.Repositories.Game;
using Poe2scout.Repositories.Game.Models;
using Poe2scout.Repositories.Item;
using Poe2scout.Repositories.Item.Models;
using Poe2scout.Repositories.UniqueItem;
using Poe2scout.Repositories.UniqueItem.Models;

namespace Poe2scout.ItemSync.Worker.Tests;

internal static class TestConfig
{
  public static ItemSyncConfig Create(
    int initialBackoff = 30,
    int maximumBackoff = 900)
  {
    var configuration = new ConfigurationBuilder()
      .AddInMemoryCollection(new Dictionary<string, string?>
      {
        ["DbConnectionString"] = "Host=test",
        ["BackoffInitialSeconds"] = initialBackoff.ToString(),
        ["BackoffMaxSeconds"] = maximumBackoff.ToString()
      })
      .Build();
    return BaseConfig.FromConfig<ItemSyncConfig>(configuration);
  }
}

internal sealed class WorkerFixture
{
  public Mock<IItemSyncClient> Client { get; } = new();
  public Mock<IGameRepository> Games { get; } = new();
  public Mock<IItemRepository> Items { get; } = new();
  public Mock<IUniqueItemRepository> UniqueItems { get; } = new();
  public Mock<ICurrencyItemRepository> CurrencyItems { get; } = new();
  public Game Game { get; } = new(2, "poe2", "Path of Exile 2", "poe2", 7);
  public ItemSyncWorker Worker { get; }

  public WorkerFixture(Func<TimeSpan, CancellationToken, Task>? delay = null)
  {
    Games.Setup(repository => repository.GetGames()).ReturnsAsync([Game]);
    Client.Setup(repository => repository.GetItemsAsync(
        It.IsAny<string>(), It.IsAny<CancellationToken>()))
      .ReturnsAsync(new ItemFeedResponse { Result = [] });
    Client.Setup(repository => repository.GetCurrenciesAsync(
        It.IsAny<string>(), It.IsAny<CancellationToken>()))
      .ReturnsAsync(new CurrencyFeedResponse { Result = [] });

    Items.Setup(repository => repository.GetAllItemTypes()).ReturnsAsync([]);
    Items.Setup(repository => repository.GetAllBaseItems(2)).ReturnsAsync([]);
    Items.Setup(repository => repository.GetAllItemCategories())
      .ReturnsAsync([new ItemCategory(1, "currency", "Currency")]);
    Items.Setup(repository => repository.CreateItemCategory(It.IsAny<CreateItemCategoryModel>()))
      .ReturnsAsync(2);
    Items.Setup(repository => repository.CreateItemType(It.IsAny<CreateItemTypeModel>()))
      .ReturnsAsync(3);
    Items.Setup(repository => repository.CreateBaseItem(It.IsAny<CreateBaseItemModel>()))
      .ReturnsAsync(4);
    Items.Setup(repository => repository.CreateItem(It.IsAny<CreateItemModel>()))
      .ReturnsAsync(5);

    UniqueItems.Setup(repository => repository.GetAllUniqueItems(2)).ReturnsAsync([]);
    UniqueItems.Setup(repository => repository.CreateUniqueItem(It.IsAny<CreateUniqueItemModel>()))
      .ReturnsAsync(6);

    CurrencyItems.Setup(repository => repository.GetAllCurrencyCategories()).ReturnsAsync([]);
    CurrencyItems.Setup(repository => repository.GetAllCurrencyItems(2)).ReturnsAsync([]);
    CurrencyItems.Setup(repository => repository.CreateCurrencyCategory(
        It.IsAny<CreateCurrencyCategoryModel>())).ReturnsAsync(7);
    CurrencyItems.Setup(repository => repository.CreateCurrencyItem(
        It.IsAny<CreateCurrencyItemModel>()))
      .ReturnsAsync(new CreateCurrencyItemResult(true, 8, null));

    Worker = new ItemSyncWorker(
      TestConfig.Create(),
      Client.Object,
      Games.Object,
      Items.Object,
      UniqueItems.Object,
      CurrencyItems.Object,
      delay ?? ((_, _) => Task.CompletedTask));
  }
}
