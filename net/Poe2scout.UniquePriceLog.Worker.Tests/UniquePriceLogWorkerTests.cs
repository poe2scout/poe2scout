using System.Net;
using Moq;
using Poe2scout.Repositories.PriceLog.Models;
using Poe2scout.UniquePriceLog.Worker;

namespace Poe2scout.UniquePriceLog.Worker.Tests;

public class UniquePriceLogWorkerTests
{
  [Fact]
  public async Task ProcessesQuotesConvertsCurrencyAndRecordsLowestPrice()
  {
    var fixture = new WorkerFixture();
    fixture.Client
      .SetupSequence(client => client.SearchUniqueAsync(
        fixture.UniqueItem,
        fixture.League,
        It.IsAny<string>(),
        It.IsAny<CancellationToken>()))
      .ReturnsAsync(WorkerFixture.Search(2))
      .ReturnsAsync(WorkerFixture.Search(4))
      .ReturnsAsync(new TradeSearchResponse("query-id", [], 0));
    fixture.Client
      .SetupSequence(client => client.FetchAsync(
        It.IsAny<IReadOnlyList<string>>(),
        "query-id",
        It.IsAny<CancellationToken>()))
      .ReturnsAsync(WorkerFixture.Fetch(5))
      .ReturnsAsync(WorkerFixture.Fetch(.5));
    RecordPriceModel? recorded = null;
    fixture.PriceLogs
      .Setup(repository => repository.RecordPrice(It.IsAny<RecordPriceModel>()))
      .Callback<RecordPriceModel>(price => recorded = price)
      .Returns(Task.CompletedTask);

    await fixture.Worker.RunIteration(CancellationToken.None);

    Assert.NotNull(recorded);
    Assert.Equal(101, recorded.ItemId);
    Assert.Equal(5, recorded.Price);
    Assert.Equal(6, recorded.Quantity);
    fixture.UniqueItems.Verify(
      repository => repository.SetUniqueItemMetadata(It.IsAny<Dictionary<string, object>>(), 1),
      Times.Exactly(2));
  }

  [Fact]
  public async Task DeactivatesDelistedItem()
  {
    var fixture = new WorkerFixture();
    fixture.Client
      .Setup(client => client.SearchUniqueAsync(
        fixture.UniqueItem,
        fixture.League,
        It.IsAny<string>(),
        It.IsAny<CancellationToken>()))
      .ThrowsAsync(new UniqueItemDelistedException(1, fixture.UniqueItem.Name));

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.UniqueItems.Verify(repository => repository.SetUniqueItemCurrent(1, false), Times.Once);
    fixture.PriceLogs.Verify(
      repository => repository.RecordPrice(It.IsAny<RecordPriceModel>()),
      Times.Never);
  }

  [Fact]
  public async Task PropagatesGenericTradeFailures()
  {
    var fixture = new WorkerFixture();
    fixture.Client
      .Setup(client => client.SearchUniqueAsync(
        fixture.UniqueItem,
        fixture.League,
        It.IsAny<string>(),
        It.IsAny<CancellationToken>()))
      .ThrowsAsync(new TradeClientException(
        "Client error",
        HttpStatusCode.BadRequest,
        "validation failure"));

    await Assert.ThrowsAsync<TradeClientException>(
      () => fixture.Worker.RunIteration(CancellationToken.None));
  }

  [Fact]
  public async Task SkipsAlreadyFetchedItems()
  {
    var fixture = new WorkerFixture();
    fixture.Services
      .Setup(repository => repository.GetFetchedItemIds(It.IsAny<string>(), 23))
      .ReturnsAsync([101]);

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.Client.VerifyNoOtherCalls();
    fixture.PriceLogs.Verify(
      repository => repository.RecordPrice(It.IsAny<RecordPriceModel>()),
      Times.Never);
  }

  [Fact]
  public async Task SynchronizesMissingCurrencyMetadataAndIcon()
  {
    var fixture = new WorkerFixture();
    fixture.UniqueItems.Setup(repository => repository.GetCurrentUniqueItems(2))
      .ReturnsAsync([]);
    fixture.Items.Setup(repository => repository.GetAllItems(2))
      .ReturnsAsync([new Poe2scout.Repositories.Item.Models.Item(999, 1, "currency")]);
    fixture.CurrencyItems.Setup(repository => repository.GetAllCurrencyItems(2))
      .ReturnsAsync([
        new Poe2scout.Models.CurrencyItem(2, 102, 1, "chaos", "Chaos Orb", "currency", null, null)
      ]);
    fixture.Client
      .Setup(client => client.SearchCurrencyAsync(
        It.IsAny<Poe2scout.Models.CurrencyItem>(),
        fixture.League,
        It.IsAny<CancellationToken>()))
      .ReturnsAsync(WorkerFixture.Search());
    fixture.Client
      .Setup(client => client.FetchAsync(
        It.IsAny<IReadOnlyList<string>>(),
        "query-id",
        It.IsAny<CancellationToken>()))
      .ReturnsAsync(WorkerFixture.Fetch(
        1,
        "{\"typeLine\":\"Chaos Orb\",\"baseType\":\"Chaos Orb\",\"icon\":\"icon-url\",\"maxStackSize\":20,\"descrText\":\"Description\"}"));

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.CurrencyItems.Verify(
      repository => repository.SetCurrencyItemMetadata(It.IsAny<Dictionary<string, object>>(), 2),
      Times.Once);
    fixture.CurrencyItems.Verify(
      repository => repository.UpdateCurrencyIconUrl("icon-url", 2),
      Times.Once);
  }

  [Fact]
  public void BindsConfigUsingSharedBaseConfig()
  {
    var config = TestConfig.Create(7, 77);

    Assert.Equal("Host=test", config.DbConnectionString);
    Assert.Equal(7, config.BackoffInitialSeconds);
    Assert.Equal(77, config.BackoffMaxSeconds);
  }

  [Fact]
  public async Task UsesConfiguredInitialBackoffAfterIterationFailure()
  {
    using var cancellation = new CancellationTokenSource();
    var delays = new List<TimeSpan>();
    var backoffApplied = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
    var fixture = new WorkerFixture((duration, _) =>
    {
      delays.Add(duration);
      backoffApplied.SetResult();
      cancellation.Cancel();
      return Task.CompletedTask;
    });
    fixture.Leagues
      .Setup(repository => repository.GetLeague(23))
      .ThrowsAsync(new InvalidOperationException("failure"));

    await fixture.Worker.StartAsync(cancellation.Token);
    await backoffApplied.Task.WaitAsync(TimeSpan.FromSeconds(1));
    await fixture.Worker.StopAsync(CancellationToken.None);

    Assert.Equal([TimeSpan.FromSeconds(30)], delays);
  }
}
