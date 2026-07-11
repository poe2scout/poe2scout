using Moq;
using Poe2scout.ItemSync.Worker;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem.Models;
using Poe2scout.Repositories.Item.Models;

namespace Poe2scout.ItemSync.Worker.Tests;

public class ItemSyncWorkerTests
{
  [Fact]
  public void BindsConfigUsingSharedBaseConfig()
  {
    var config = TestConfig.Create(7, 77);

    Assert.Equal("Host=test", config.DbConnectionString);
    Assert.Equal(7, config.BackoffInitialSeconds);
    Assert.Equal(77, config.BackoffMaxSeconds);
  }

  [Fact]
  public async Task CreatesMissingItemEntitiesInPythonOrder()
  {
    var fixture = new WorkerFixture();
    fixture.Client.Setup(client => client.GetItemsAsync("poe2", It.IsAny<CancellationToken>()))
      .ReturnsAsync(new ItemFeedResponse
      {
        Result =
        [
          new ItemFeedCategory
          {
            Id = "body_armour",
            Label = "Body Armour",
            Entries =
            [
              new ItemFeedEntry
              {
                Type = "Test Armour",
                Name = "Test Unique",
                Text = "Test description"
              }
            ]
          }
        ]
      });

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.Items.Verify(repository => repository.CreateItemCategory(
      new CreateItemCategoryModel("body_armour", "Body Armour")), Times.Once);
    fixture.Items.Verify(repository => repository.CreateItemType(
      new CreateItemTypeModel("Test Armour", 2)), Times.Once);
    fixture.Items.Verify(repository => repository.CreateBaseItem(
      new CreateBaseItemModel(2, 3, null, null)), Times.Once);
    fixture.Items.Verify(repository => repository.CreateItem(
      new CreateItemModel(4, "base")), Times.Once);
    fixture.Items.Verify(repository => repository.CreateItem(
      new CreateItemModel(4, "unique")), Times.Once);
    fixture.UniqueItems.Verify(repository => repository.CreateUniqueItem(
      new CreateUniqueItemModel(5, null, "Test description", "Test Unique")), Times.Once);
  }

  [Fact]
  public async Task ReactivatesInactiveUniqueWithoutCreatingAnotherUnique()
  {
    var fixture = new WorkerFixture();
    fixture.Items.Setup(repository => repository.GetAllItemCategories())
      .ReturnsAsync([new ItemCategory(1, "body_armour", "Body Armour"), new ItemCategory(2, "currency", "Currency")]);
    fixture.Items.Setup(repository => repository.GetAllItemTypes())
      .ReturnsAsync([new ItemType(3, "Test Armour", 1)]);
    fixture.Items.Setup(repository => repository.GetAllBaseItems(2))
      .ReturnsAsync([new BaseItem(4, 3, 2, null, null)]);
    fixture.UniqueItems.Setup(repository => repository.GetAllUniqueItems(2))
      .ReturnsAsync([new UniqueItem(6, 5, null, "Description", "Test Unique", "body_armour", null, "Test Armour", false, false)]);
    fixture.Client.Setup(client => client.GetItemsAsync("poe2", It.IsAny<CancellationToken>()))
      .ReturnsAsync(new ItemFeedResponse
      {
        Result =
        [
          new ItemFeedCategory
          {
            Id = "body_armour",
            Label = "Body Armour",
            Entries = [new ItemFeedEntry { Type = "Test Armour", Name = "Test Unique", Text = "Description" }]
          }
        ]
      });

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.UniqueItems.Verify(repository => repository.SetUniqueItemCurrent(6, true), Times.Once);
    fixture.UniqueItems.Verify(repository => repository.CreateUniqueItem(It.IsAny<CreateUniqueItemModel>()), Times.Never);
    fixture.Items.Verify(repository => repository.CreateItem(It.IsAny<CreateItemModel>()), Times.Never);
  }

  [Fact]
  public async Task FailsWhenUniqueItemHasNoText()
  {
    var fixture = new WorkerFixture();
    fixture.Client.Setup(client => client.GetItemsAsync("poe2", It.IsAny<CancellationToken>()))
      .ReturnsAsync(new ItemFeedResponse
      {
        Result =
        [
          new ItemFeedCategory
          {
            Id = "body_armour",
            Label = "Body Armour",
            Entries = [new ItemFeedEntry { Type = "Test Armour", Name = "Test Unique", Text = null }]
          }
        ]
      });

    await Assert.ThrowsAsync<InvalidOperationException>(() =>
      fixture.Worker.RunIteration(CancellationToken.None));
  }

  [Fact]
  public async Task CreatesCurrencyWithLowercaseCategoryMetadataAndFullIconUrl()
  {
    var fixture = new WorkerFixture();
    fixture.Client.Setup(client => client.GetCurrenciesAsync("poe2", It.IsAny<CancellationToken>()))
      .ReturnsAsync(new CurrencyFeedResponse
      {
        Result =
        [
          new CurrencyFeedCategory
          {
            Id = "CURRENCY_ORBS",
            Label = "Currency Orbs",
            Entries = [new CurrencyFeedEntry { Id = "exalted", Text = "Exalted Orb", Image = "items/exalted.png" }]
          }
        ]
      });

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.CurrencyItems.Verify(repository => repository.CreateCurrencyCategory(
      new CreateCurrencyCategoryModel("currency_orbs", "Currency Orbs")), Times.Once);
    fixture.Items.Verify(repository => repository.CreateBaseItem(
      It.Is<CreateBaseItemModel>(model =>
        model.GameId == 2
        && model.ItemTypeId == 3
        && model.IconUrl == "items/exalted.png"
        && model.ItemMetadata!["id"].Equals("exalted")
        && model.ItemMetadata["text"].Equals("Exalted Orb"))), Times.Once);
    fixture.CurrencyItems.Verify(repository => repository.CreateCurrencyItem(
      new CreateCurrencyItemModel(5, 7, "exalted", "Exalted Orb", "https://web.poecdn.com/items/exalted.png")), Times.Once);
  }

  [Fact]
  public async Task SkipsUnlabelledCategoriesAndEmptyCurrencies()
  {
    var fixture = new WorkerFixture();
    fixture.Client.Setup(client => client.GetCurrenciesAsync("poe2", It.IsAny<CancellationToken>()))
      .ReturnsAsync(new CurrencyFeedResponse
      {
        Result =
        [
          new CurrencyFeedCategory
          {
            Id = "unlabelled",
            Label = null,
            Entries = [new CurrencyFeedEntry { Id = "ignored", Text = "Ignored" }]
          },
          new CurrencyFeedCategory
          {
            Id = "empty",
            Label = "Empty",
            Entries = [new CurrencyFeedEntry { Id = "ignored", Text = string.Empty }]
          }
        ]
      });

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.CurrencyItems.Verify(repository => repository.CreateCurrencyCategory(
      It.IsAny<CreateCurrencyCategoryModel>()), Times.Never);
    fixture.Items.Verify(repository => repository.CreateItemType(
      It.IsAny<CreateItemTypeModel>()), Times.Never);
  }

  [Fact]
  public async Task ProcessesGamesSequentiallyAndWaitsOneDayAfterSuccess()
  {
    var delays = new List<TimeSpan>();
    var fixture = new WorkerFixture((duration, _) =>
    {
      delays.Add(duration);
      return Task.CompletedTask;
    });
    var secondGame = new Poe2scout.Repositories.Game.Models.Game(3, "poe2-alt", "Alternate", "alternate", 8);
    fixture.Games.Setup(repository => repository.GetGames()).ReturnsAsync([fixture.Game, secondGame]);
    var identifiers = new List<string>();
    fixture.Client.Setup(client => client.GetItemsAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
      .Callback<string, CancellationToken>((identifier, _) => identifiers.Add(identifier))
      .ReturnsAsync(new ItemFeedResponse { Result = [] });

    await fixture.Worker.RunIteration(CancellationToken.None);

    Assert.Equal(["poe2", "alternate"], identifiers);
    Assert.Equal([TimeSpan.FromDays(1)], delays);
  }

  [Fact]
  public async Task UsesBackoffAfterFailuresAndResetsAfterSuccess()
  {
    using var cancellation = new CancellationTokenSource();
    var delays = new List<TimeSpan>();
    var completed = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
    var fixture = new WorkerFixture((duration, _) =>
    {
      delays.Add(duration);
      if (duration == TimeSpan.FromSeconds(60))
      {
        cancellation.Cancel();
        completed.SetResult();
      }

      return Task.CompletedTask;
    });
    fixture.Games.SetupSequence(repository => repository.GetGames())
      .ReturnsAsync([])
      .ThrowsAsync(new InvalidOperationException("first failure"))
      .ThrowsAsync(new InvalidOperationException("second failure"));

    await fixture.Worker.StartAsync(cancellation.Token);
    await completed.Task.WaitAsync(TimeSpan.FromSeconds(1));
    await fixture.Worker.StopAsync(CancellationToken.None);

    Assert.Equal([TimeSpan.FromDays(1), TimeSpan.FromSeconds(30), TimeSpan.FromSeconds(60)], delays);
  }
}
