using Moq;
using Poe2scout.CurrencyExchange.Worker;
using Poe2scout.Repositories.CurrencyExchange.Models;
using Poe2scout.Repositories.PriceLog.Models;
using Poe2scout.Repositories.Service.Models;

namespace Poe2scout.CurrencyExchange.Worker.Tests;

public class CurrencyExchangeWorkerTests
{
  [Fact]
  public void BindsConfigUsingSharedBaseConfig()
  {
    var config = TestConfig.Create(7, 77);

    Assert.Equal("Host=test", config.DbConnectionString);
    Assert.Equal("client-id", config.PoeApiClientId);
    Assert.Equal("client-secret", config.PoeApiClientSecret);
    Assert.Equal(7, config.BackoffInitialSeconds);
    Assert.Equal(77, config.BackoffMaxSeconds);
  }

  [Fact]
  public async Task ProcessesSnapshotAndAdvancesCacheAfterSuccessfulRealms()
  {
    var fixture = new WorkerFixture();
    CurrencyExchangeSnapshot? captured = null;
    fixture.Exchange
      .Setup(repository => repository.CreateSnapshot(It.IsAny<CurrencyExchangeSnapshot>()))
      .Callback<CurrencyExchangeSnapshot>(snapshot => captured = snapshot)
      .ReturnsAsync(1);

    await fixture.Worker.RunIteration(CancellationToken.None);

    Assert.NotNull(captured);
    Assert.Equal(fixture.CurrentEpoch, captured.Epoch);
    Assert.Equal(10m, captured.Volume);
    Assert.Equal(7m, captured.MarketCap);
    var pair = Assert.Single(captured.Pairs);
    Assert.Equal(100, pair.CurrencyOneItemId);
    Assert.Equal(101, pair.CurrencyTwoItemId);
    Assert.Equal(10m, pair.Volume);
    Assert.Equal(1m, pair.CurrencyOneData.RelativePrice);
    Assert.Equal(.1m, pair.CurrencyTwoData.RelativePrice);
    Assert.Equal(5m, pair.CurrencyOneData.StockValue);
    Assert.Equal(2m, pair.CurrencyTwoData.StockValue);
    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue("CurrencyExchange", fixture.CurrentEpoch),
      Times.Once);
    fixture.Exchange.Verify(repository => repository.UpdatePairHistories(), Times.Once);
  }

  [Fact]
  public async Task RequestsAnInitialSnapshotWithoutAnEpochWhenExchangeCacheIsMissing()
  {
    var fixture = new WorkerFixture();
    fixture.Services.Setup(repository => repository.GetServiceCacheValue("CurrencyExchange"))
      .ReturnsAsync((ServiceCacheValue?)null);
    fixture.Client.Reset();
    fixture.Client.Setup(client => client.GetSnapshot(
        "pc",
        null,
        It.IsAny<CancellationToken>()))
      .ReturnsAsync(new CurrencyExchangeResponse(
        fixture.CurrentEpoch + 3600,
        [Pair("exalted|chaos", 10, 100, 5, 20)]));

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.Client.Verify(client => client.GetSnapshot(
      "pc",
      null,
      It.IsAny<CancellationToken>()), Times.Once);
    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue("CurrencyExchange", fixture.CurrentEpoch),
      Times.Once);
  }

  [Fact]
  public async Task WaitsWhenPriceFetchHasNotMovedAhead()
  {
    var fixture = new WorkerFixture();
    fixture.Services.Setup(repository => repository.GetServiceCacheValue("PriceFetch_Currency"))
      .ReturnsAsync(new ServiceCacheValue(fixture.CurrentEpoch - 3600));

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.Client.VerifyNoOtherCalls();
    Assert.Contains(TimeSpan.FromMinutes(10), fixture.Delays);
    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue(It.IsAny<string>(), It.IsAny<int>()),
      Times.Never);
  }

  [Fact]
  public async Task MissingPriceLogsDoesNotAdvanceCacheOrWriteSnapshot()
  {
    var fixture = new WorkerFixture();
    fixture.Services.Setup(repository => repository.GetCurrencyFetchStatus(It.IsAny<DateTime>()))
      .ReturnsAsync(false);

    await fixture.Worker.RunIteration(CancellationToken.None);

    Assert.Contains(TimeSpan.FromMinutes(10), fixture.Delays);
    fixture.Exchange.Verify(
      repository => repository.CreateSnapshot(It.IsAny<CurrencyExchangeSnapshot>()),
      Times.Never);
    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue(It.IsAny<string>(), It.IsAny<int>()),
      Times.Never);
    fixture.Exchange.Verify(repository => repository.UpdatePairHistories(), Times.Never);
  }

  [Fact]
  public async Task ExistingSnapshotLeaguesAreSkipped()
  {
    var fixture = new WorkerFixture();
    fixture.Exchange.Setup(repository => repository.GetExistingSnapshotLeagueIds(
        fixture.CurrentEpoch,
        1))
      .ReturnsAsync([1]);

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.CurrencyItems.Verify(repository => repository.GetAllCurrencyItems(It.IsAny<int>()), Times.Never);
    fixture.PriceLogs.Verify(repository => repository.GetItemPricesInRange(
        It.IsAny<List<int>>(),
        It.IsAny<int>(),
        It.IsAny<int>(),
        It.IsAny<DateTime>(),
        It.IsAny<DateTime>()), Times.Never);
    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue("CurrencyExchange", fixture.CurrentEpoch),
      Times.Once);
  }

  [Fact]
  public async Task UnknownCurrenciesAreFilteredFromSnapshotPairs()
  {
    var fixture = new WorkerFixture();
    fixture.Client.Reset();
    fixture.Client.Setup(client => client.GetSnapshot(
        "pc",
        fixture.CurrentEpoch,
        It.IsAny<CancellationToken>()))
      .ReturnsAsync(new CurrencyExchangeResponse(
        fixture.CurrentEpoch + 3600,
        [
          Pair("exalted|chaos", 10, 100, 5, 20),
          Pair("exalted|unknown", 10, 20, 5, 5)
        ]));
    CurrencyExchangeSnapshot? captured = null;
    fixture.Exchange
      .Setup(repository => repository.CreateSnapshot(It.IsAny<CurrencyExchangeSnapshot>()))
      .Callback<CurrencyExchangeSnapshot>(snapshot => captured = snapshot)
      .ReturnsAsync(1);

    await fixture.Worker.RunIteration(CancellationToken.None);

    Assert.NotNull(captured);
    Assert.Single(captured.Pairs);
  }

  [Fact]
  public async Task UsesSecondCurrencyWhenPriceQuantitiesAreTied()
  {
    var fixture = new WorkerFixture();
    fixture.Client.Reset();
    fixture.Client.Setup(client => client.GetSnapshot(
        "pc",
        fixture.CurrentEpoch,
        It.IsAny<CancellationToken>()))
      .ReturnsAsync(new CurrencyExchangeResponse(
        fixture.CurrentEpoch + 3600,
        [Pair("exalted|chaos", 10, 200, 5, 20)]));
    fixture.PriceLogs.Setup(repository => repository.GetItemPricesInRange(
        It.IsAny<List<int>>(),
        1,
        1,
        It.IsAny<DateTime>(),
        It.IsAny<DateTime>()))
      .ReturnsAsync(
      [
        new ItemPriceInRange(100, 1m, 10m),
        new ItemPriceInRange(101, .1m, 10m)
      ]);
    CurrencyExchangeSnapshot? captured = null;
    fixture.Exchange
      .Setup(repository => repository.CreateSnapshot(It.IsAny<CurrencyExchangeSnapshot>()))
      .Callback<CurrencyExchangeSnapshot>(snapshot => captured = snapshot)
      .ReturnsAsync(1);

    await fixture.Worker.RunIteration(CancellationToken.None);

    Assert.NotNull(captured);
    Assert.Equal(20m, Assert.Single(captured.Pairs).Volume);
  }

  [Fact]
  public async Task SkipsSnapshotWhenAllPairValuesAndStockValuesAreZero()
  {
    var fixture = new WorkerFixture();
    fixture.Client.Reset();
    fixture.Client.Setup(client => client.GetSnapshot(
        "pc",
        fixture.CurrentEpoch,
        It.IsAny<CancellationToken>()))
      .ReturnsAsync(new CurrencyExchangeResponse(
        fixture.CurrentEpoch + 3600,
        [Pair("exalted|chaos", 0, 0, 0, 0)]));

    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.Exchange.Verify(
      repository => repository.CreateSnapshot(It.IsAny<CurrencyExchangeSnapshot>()),
      Times.Never);
    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue("CurrencyExchange", fixture.CurrentEpoch),
      Times.Once);
  }

  [Fact]
  public async Task RealmFailureDoesNotAdvanceCache()
  {
    var fixture = new WorkerFixture();
    fixture.Client.Setup(client => client.GetSnapshot(
        "pc",
        fixture.CurrentEpoch,
        It.IsAny<CancellationToken>()))
      .ThrowsAsync(new PoeCurrencyExchangeException("failure", System.Net.HttpStatusCode.InternalServerError));

    await Assert.ThrowsAsync<PoeCurrencyExchangeException>(
      () => fixture.Worker.RunIteration(CancellationToken.None));

    fixture.Services.Verify(
      repository => repository.SetServiceCacheValue(It.IsAny<string>(), It.IsAny<int>()),
      Times.Never);
    fixture.Exchange.Verify(repository => repository.UpdatePairHistories(), Times.Never);
  }

  [Fact]
  public async Task UsesBackoffAfterFailureAndStopsWhenCancellationIsRequested()
  {
    using var cancellation = new CancellationTokenSource();
    var completed = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
    var delays = new List<TimeSpan>();
    var fixture = new WorkerFixture();
    fixture.Services.Setup(repository => repository.GetServiceCacheValue(It.IsAny<string>()))
      .ThrowsAsync(new InvalidOperationException("failure"));
    var worker = new CurrencyExchangeWorker(
      TestConfig.Create(),
      fixture.Client.Object,
      fixture.Services.Object,
      fixture.Realms.Object,
      fixture.Leagues.Object,
      fixture.CurrencyItems.Object,
      fixture.PriceLogs.Object,
      fixture.Exchange.Object,
      (duration, _) =>
      {
        delays.Add(duration);
        if (duration == TimeSpan.FromSeconds(30))
        {
          cancellation.Cancel();
          completed.SetResult();
        }

        return Task.CompletedTask;
      });

    await worker.StartAsync(cancellation.Token);
    await completed.Task.WaitAsync(TimeSpan.FromSeconds(1));
    await worker.StopAsync(CancellationToken.None);

    Assert.Equal([TimeSpan.FromSeconds(30)], delays);
  }

  public static TradingPair Pair(
    string marketId,
    int currencyOneVolume,
    int currencyTwoVolume,
    int currencyOneStock,
    int currencyTwoStock)
    => new(
      "Test League",
      marketId,
      new Dictionary<string, int>
      {
        [marketId.Split('|')[0]] = currencyOneVolume,
        [marketId.Split('|')[1]] = currencyTwoVolume
      },
      new Dictionary<string, int>
      {
        [marketId.Split('|')[0]] = currencyOneStock,
        [marketId.Split('|')[1]] = currencyTwoStock
      });
}
