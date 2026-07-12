using Moq;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.Game;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.PriceLog.Models;
using Poe2scout.Repositories.Realm;
using Poe2scout.Repositories.Realm.Models;
using Poe2scout.Repositories.Service;
using Poe2scout.Repositories.Service.Models;

namespace Poe2scout.CurrencyPriceLog.Worker.Tests;

public class CurrencyPriceLogWorkerIterationTests
{
  [Fact]
  public async Task ProcessesSnapshotAndAdvancesCacheAfterSuccessfulRealms()
  {
    var fixture = new WorkerFixture();
    var capturedPrices = new List<RecordPriceModel>();
    fixture.PriceLogs
      .Setup(repository => repository.RecordPriceBulk(It.IsAny<List<RecordPriceModel>>(), fixture.CurrentEpoch))
      .Callback<List<RecordPriceModel>, int>((prices, _) => capturedPrices = prices)
      .Returns(Task.CompletedTask);

    await fixture.Worker.RunIteration(CancellationToken.None);

    Assert.Collection(
      capturedPrices.OrderBy(price => price.ItemId),
      price =>
      {
        Assert.Equal(100, price.ItemId);
        Assert.Equal(1, price.Price);
        Assert.Equal(10, price.Quantity);
      },
      price =>
      {
        Assert.Equal(101, price.ItemId);
        Assert.Equal(.1, price.Price, 12);
        Assert.Equal(100, price.Quantity);
      });
    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue("PriceFetch_Currency", fixture.CurrentEpoch),
      Times.Once);
  }

  [Fact]
  public async Task SkipsLeagueWhenTimestampWasAlreadyRecorded()
  {
    var fixture = new WorkerFixture();
    fixture.PriceLogs
      .Setup(repository => repository.GetPricesChecked(fixture.CurrentEpoch, 1, 1))
      .ReturnsAsync(true);

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.PriceLogs.Verify(
      repository => repository.RecordPriceBulk(It.IsAny<List<RecordPriceModel>>(), It.IsAny<int>()),
      Times.Never);
    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue("PriceFetch_Currency", fixture.CurrentEpoch),
      Times.Once);
  }

  [Fact]
  public async Task EmptyMarketAdvancesCacheWithoutLoadingRealmData()
  {
    var fixture = new WorkerFixture(new CurrencyExchangeResponse(5000, []));

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.Leagues.Verify(repository => repository.GetLeagues(It.IsAny<int>()), Times.Never);
    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue("PriceFetch_Currency", fixture.CurrentEpoch),
      Times.Once);
  }

  [Fact]
  public async Task RealmFailureDoesNotAdvanceCache()
  {
    var fixture = new WorkerFixture();
    fixture.Client
      .Setup(client => client.GetSnapshot("pc", fixture.CurrentEpoch, It.IsAny<CancellationToken>()))
      .ThrowsAsync(new PoeApiException("failure", System.Net.HttpStatusCode.InternalServerError));

    await Assert.ThrowsAsync<PoeApiException>(() => fixture.Worker.RunIteration(CancellationToken.None));

    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue(It.IsAny<string>(), It.IsAny<int>()),
      Times.Never);
  }

  [Fact]
  public async Task UsesHistoricalBridgePriceAndFiltersUnknownItems()
  {
    var fixture = new WorkerFixture(new CurrencyExchangeResponse(5000,
    [
      CurrencyPriceCalculatorTests.Pair("exalted|chaos", new() { ["exalted"] = 10, ["chaos"] = 100 }),
      CurrencyPriceCalculatorTests.Pair("chaos|divine", new() { ["chaos"] = 300, ["divine"] = 1 }),
      CurrencyPriceCalculatorTests.Pair("divine|unknown", new() { ["divine"] = 1, ["unknown"] = 2 })
    ]));
    fixture.Games.Setup(repository => repository.GetBridgeCurrencies(1)).ReturnsAsync(
    [
      CurrencyPriceCalculatorTests.Bridge("chaos", 1),
      CurrencyPriceCalculatorTests.Bridge("divine", 2)
    ]);
    fixture.PriceLogs
      .Setup(repository => repository.GetItemPricesBefore(
        It.IsAny<List<int>>(), 1, 1, fixture.CurrentEpoch))
      .ReturnsAsync([new ItemPriceBefore(1, 0), new ItemPriceBefore(2, 28)]);
    List<RecordPriceModel>? captured = null;
    fixture.PriceLogs
      .Setup(repository => repository.RecordPriceBulk(It.IsAny<List<RecordPriceModel>>(), fixture.CurrentEpoch))
      .Callback<List<RecordPriceModel>, int>((prices, _) => captured = prices)
      .Returns(Task.CompletedTask);

    await fixture.Worker.RunIteration(CancellationToken.None);

    Assert.NotNull(captured);
    Assert.Contains(captured, price => price.ItemId == 102 && price.Price == 28);
    Assert.DoesNotContain(captured, price => price.ItemId is not (100 or 101 or 102));
  }

  private sealed class WorkerFixture
  {
    public Mock<IPoeCurrencyExchangeClient> Client { get; } = new();
    public Mock<IServiceRepository> Services { get; } = new();
    public Mock<IRealmRepository> Realms { get; } = new();
    public Mock<ILeagueRepository> Leagues { get; } = new();
    public Mock<ICurrencyItemRepository> CurrencyItems { get; } = new();
    public Mock<IGameRepository> Games { get; } = new();
    public Mock<IPriceLogRepository> PriceLogs { get; } = new();
    public int CurrentEpoch { get; }
    public CurrencyPriceLogWorker Worker { get; }

    public WorkerFixture(CurrencyExchangeResponse? response = null)
    {
      CurrentEpoch = checked((int)(DateTime.UtcNow - DateTime.UnixEpoch).TotalSeconds - 4000);
      response ??= new CurrencyExchangeResponse(5000,
      [
        CurrencyPriceCalculatorTests.Pair(
          "exalted|chaos",
          new Dictionary<string, int> { ["exalted"] = 10, ["chaos"] = 100 })
      ]);
      Services.Setup(repository => repository.GetServiceCacheValue("PriceFetch_Currency"))
        .ReturnsAsync(new ServiceCacheValue(CurrentEpoch - 60 * 60));
      Services.Setup(repository => repository.SetServiceCacheValue(It.IsAny<string>(), It.IsAny<int>()))
        .Returns(Task.CompletedTask);
      Realms.Setup(repository => repository.GetRealms()).ReturnsAsync([new Realm(1, 1, "pc")]);
      Client.Setup(client => client.GetSnapshot("pc", CurrentEpoch, It.IsAny<CancellationToken>()))
        .ReturnsAsync(response);
      Leagues.Setup(repository => repository.GetLeagues(1)).ReturnsAsync([CurrencyPriceCalculatorTests.League()]);
      CurrencyItems.Setup(repository => repository.GetAllCurrencyItems(1)).ReturnsAsync(
      [
        Item(100, "exalted"),
        Item(101, "chaos"),
        Item(102, "divine")
      ]);
      Games.Setup(repository => repository.GetBridgeCurrencies(1)).ReturnsAsync(
        [CurrencyPriceCalculatorTests.Bridge("chaos", 1)]);
      PriceLogs.Setup(repository => repository.GetPricesChecked(CurrentEpoch, 1, 1)).ReturnsAsync(false);
      PriceLogs.Setup(repository => repository.GetItemPricesBefore(It.IsAny<List<int>>(), 1, 1, CurrentEpoch))
        .ReturnsAsync([new ItemPriceBefore(1, 0)]);
      PriceLogs.Setup(repository => repository.RecordPriceBulk(It.IsAny<List<RecordPriceModel>>(), CurrentEpoch))
        .Returns(Task.CompletedTask);

      Worker = new CurrencyPriceLogWorker(
        TestConfig.Create(),
        Client.Object,
        Services.Object,
        Realms.Object,
        Leagues.Object,
        CurrencyItems.Object,
        Games.Object,
        PriceLogs.Object);
    }

    private static CurrencyItem Item(int itemId, string apiId)
      => new(itemId, itemId, 1, apiId, apiId, "currency", null, null);
  }
}
