using Microsoft.Extensions.Configuration;
using Moq;
using Poe2scout.CurrencyExchange.Worker;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyExchange;
using Poe2scout.Repositories.CurrencyExchange.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.League.Models;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.PriceLog.Models;
using Poe2scout.Repositories.Realm;
using Poe2scout.Repositories.Realm.Models;
using Poe2scout.Repositories.Service;
using Poe2scout.Repositories.Service.Models;

namespace Poe2scout.CurrencyExchange.Worker.Tests;

internal static class TestConfig
{
  public static CurrencyExchangeConfig Create(
    int initialBackoff = 30,
    int maximumBackoff = 900)
  {
    var configuration = new ConfigurationBuilder()
      .AddInMemoryCollection(new Dictionary<string, string?>
      {
        ["DbConnectionString"] = "Host=test",
        ["PoeApiClientId"] = "client-id",
        ["PoeApiClientSecret"] = "client-secret",
        ["BackoffInitialSeconds"] = initialBackoff.ToString(),
        ["BackoffMaxSeconds"] = maximumBackoff.ToString()
      })
      .Build();

    return Poe2scout.BaseConfig.FromConfig<CurrencyExchangeConfig>(configuration);
  }
}

internal sealed class WorkerFixture
{
  public Mock<ICurrencyExchangeClient> Client { get; } = new();
  public Mock<IServiceRepository> Services { get; } = new();
  public Mock<IRealmRepository> Realms { get; } = new();
  public Mock<ILeagueRepository> Leagues { get; } = new();
  public Mock<ICurrencyItemRepository> CurrencyItems { get; } = new();
  public Mock<IPriceLogRepository> PriceLogs { get; } = new();
  public Mock<ICurrencyExchangeRepository> Exchange { get; } = new();
  public int CurrentEpoch { get; } = checked((int)DateTimeOffset.UtcNow.ToUnixTimeSeconds() - 3600);
  public List<TimeSpan> Delays { get; } = [];
  public CurrencyExchangeWorker Worker { get; }

  public WorkerFixture(CurrencyExchangeResponse? response = null)
  {
    response ??= new CurrencyExchangeResponse(
      CurrentEpoch + 3600,
      [CurrencyExchangeWorkerTests.Pair("exalted|chaos", 10, 100, 5, 20)]);

    Services.Setup(repository => repository.GetServiceCacheValue("CurrencyExchange"))
      .ReturnsAsync(new ServiceCacheValue(CurrentEpoch - 3600));
    Services.Setup(repository => repository.GetServiceCacheValue("PriceFetch_Currency"))
      .ReturnsAsync(new ServiceCacheValue(CurrentEpoch));
    Services.Setup(repository => repository.GetCurrencyFetchStatus(It.IsAny<DateTime>()))
      .ReturnsAsync(true);
    Services.Setup(repository => repository.SetServiceCacheValue(It.IsAny<string>(), It.IsAny<int>()))
      .Returns(Task.CompletedTask);

    Realms.Setup(repository => repository.GetRealms())
      .ReturnsAsync([new Realm(1, 1, "pc")]);
    Client.Setup(client => client.GetSnapshot(
        "pc",
        CurrentEpoch,
        It.IsAny<CancellationToken>()))
      .ReturnsAsync(response);
    Leagues.Setup(repository => repository.GetLeagues(1))
      .ReturnsAsync([new League(1, "Test League", "Test", 100, "exalted", "Exalted Orb", null, true)]);
    CurrencyItems.Setup(repository => repository.GetAllCurrencyItems(1))
      .ReturnsAsync(
      [
        Item(100, "exalted"),
        Item(101, "chaos")
      ]);
    Exchange.Setup(repository => repository.GetExistingSnapshotLeagueIds(
        It.IsAny<int>(),
        It.IsAny<int>()))
      .ReturnsAsync([]);
    PriceLogs.Setup(repository => repository.GetItemPricesInRange(
        It.IsAny<List<int>>(),
        1,
        1,
        It.IsAny<DateTime>(),
        It.IsAny<DateTime>()))
      .ReturnsAsync(
      [
        new ItemPriceInRange(100, 1m, 10m),
        new ItemPriceInRange(101, .1m, 100m)
      ]);
    Exchange.Setup(repository => repository.CreateSnapshot(It.IsAny<CurrencyExchangeSnapshot>()))
      .ReturnsAsync(1);
    Exchange.Setup(repository => repository.UpdatePairHistories())
      .Returns(Task.CompletedTask);

    Worker = new CurrencyExchangeWorker(
      TestConfig.Create(),
      Client.Object,
      Services.Object,
      Realms.Object,
      Leagues.Object,
      CurrencyItems.Object,
      PriceLogs.Object,
      Exchange.Object,
      (duration, _) =>
      {
        Delays.Add(duration);
        return Task.CompletedTask;
      });
  }

  public static CurrencyItem Item(int itemId, string apiId)
    => new(itemId, itemId, 1, apiId, apiId, "currency", null, null);
}
