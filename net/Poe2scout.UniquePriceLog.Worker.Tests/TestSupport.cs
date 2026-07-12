using System.Text.Json;
using Microsoft.Extensions.Configuration;
using Moq;
using Poe2scout;
using Poe2scout.Models;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.Item;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.League.Models;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.Service;
using Poe2scout.Repositories.UniqueItem;
using Poe2scout.Repositories.Service.Models;
using Poe2scout.UniquePriceLog.Worker;

namespace Poe2scout.UniquePriceLog.Worker.Tests;

internal static class TestConfig
{
  public static UniquePriceLogConfig Create(
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
    return BaseConfig.FromConfig<UniquePriceLogConfig>(configuration);
  }
}

internal sealed class WorkerFixture
{
  public Mock<IPoeTradeClient> Client { get; } = new();
  public Mock<IServiceRepository> Services { get; } = new();
  public Mock<ILeagueRepository> Leagues { get; } = new();
  public Mock<IUniqueItemRepository> UniqueItems { get; } = new();
  public Mock<ICurrencyItemRepository> CurrencyItems { get; } = new();
  public Mock<IItemRepository> Items { get; } = new();
  public Mock<IPriceLogRepository> PriceLogs { get; } = new();
  public UniquePriceLogWorker Worker { get; }
  public League League { get; } = new(23, "Standard", "Standard", 100, "exalted", "Exalted Orb", null, true);
  public UniqueItem UniqueItem { get; } = new(1, 101, null, "Test", "Test Unique", "body_armour", null, "Armour", null, true);

  public WorkerFixture(Func<TimeSpan, CancellationToken, Task>? delay = null)
  {
    Leagues.Setup(repository => repository.GetLeague(23)).ReturnsAsync(League);
    UniqueItems.Setup(repository => repository.GetCurrentUniqueItems(2))
      .ReturnsAsync([UniqueItem]);
    CurrencyItems.Setup(repository => repository.GetAllCurrencyItems(2))
      .ReturnsAsync([
        new CurrencyItem(1, 100, 1, "exalted", "Exalted Orb", "currency", null, new Dictionary<string, object>()),
        new CurrencyItem(2, 102, 1, "chaos", "Chaos Orb", "currency", "chaos-icon", new Dictionary<string, object>())
      ]);
    Services.Setup(repository => repository.GetFetchedItemIds(It.IsAny<string>(), 23))
      .ReturnsAsync([]);
    Items.Setup(repository => repository.GetAllItems(2))
      .ReturnsAsync([new Poe2scout.Repositories.Item.Models.Item(101, 1, "unique")]);
    CurrencyItems.Setup(repository => repository.GetCurrencyItem("chaos", 2))
      .ReturnsAsync(new CurrencyItem(2, 102, 1, "chaos", "Chaos Orb", "currency", "chaos-icon", null));
    PriceLogs.Setup(repository => repository.GetItemPrice(102, 23, 4, null))
      .ReturnsAsync(10);

    Worker = new UniquePriceLogWorker(
      TestConfig.Create(),
      Client.Object,
      Services.Object,
      Leagues.Object,
      UniqueItems.Object,
      CurrencyItems.Object,
      Items.Object,
      PriceLogs.Object,
      delay ?? ((_, _) => Task.CompletedTask));
  }

  public static TradeSearchResponse Search(int total = 1)
    => new("query-id", ["item-id"], total);

  public static TradeFetchResponse Fetch(double amount, string? itemJson = null)
  {
    using var document = JsonDocument.Parse(itemJson ?? "{\"name\":\"Test\"}");
    var item = document.RootElement.Clone();
    var amountDocument = JsonDocument.Parse(amount.ToString(System.Globalization.CultureInfo.InvariantCulture));
    var amountElement = amountDocument.RootElement.Clone();
    amountDocument.Dispose();
    return new TradeFetchResponse([
      new TradeResult(
        new TradeListing(new TradePrice(amountElement)),
        item)
    ]);
  }
}
