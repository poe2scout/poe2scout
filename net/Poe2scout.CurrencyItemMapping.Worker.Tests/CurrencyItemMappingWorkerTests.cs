using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging.Abstractions;
using Moq;
using Poe2scout.Repositories.Game;
using Poe2scout.Repositories.Game.Models;
using Poe2scout.Repositories.Realm;
using Poe2scout.Repositories.Realm.Models;

namespace Poe2scout.CurrencyItemMapping.Worker.Tests;

public sealed class CurrencyItemMappingWorkerTests
{
  [Fact]
  public async Task DryRunDoesNotWrite()
  {
    var fixture = new WorkerFixture(applyChanges: false);

    var reports = await fixture.Worker.RunIteration(CancellationToken.None);

    Assert.Equal(1, Assert.Single(reports).Mapped);
    fixture.Repository.Verify(
      repository => repository.Apply(
        It.IsAny<IReadOnlyList<GameMappingReport>>(),
        It.IsAny<IReadOnlyList<ConfirmedAlias>>()),
      Times.Never);
  }

  [Fact]
  public async Task ApplyModeWritesPlanAndRepeatedUnchangedRunIsIdempotent()
  {
    var fixture = new WorkerFixture(applyChanges: true);
    await fixture.Worker.RunIteration(CancellationToken.None);

    fixture.Repository.Verify(
      repository => repository.Apply(
        It.Is<IReadOnlyList<GameMappingReport>>(reports =>
          reports.Single().Assignments.Single().BaseItemTypeId == "Metadata/Known"),
        It.IsAny<IReadOnlyList<ConfirmedAlias>>()),
      Times.Once);

    fixture.Repository.Setup(repository => repository.GetCurrencies())
      .ReturnsAsync([
        new MappingCurrencyRow(
          1,
          "poe",
          1,
          1,
          "current",
          "Metadata/Known",
          "Known")
      ]);
    var secondReports = await fixture.Worker.RunIteration(CancellationToken.None);

    Assert.Equal(1, Assert.Single(secondReports).Unchanged);
  }

  [Fact]
  public async Task ConflictPreventsTransactionalApply()
  {
    var fixture = new WorkerFixture(applyChanges: true);
    fixture.Repository.Setup(repository => repository.GetCurrencies())
      .ReturnsAsync([
        new MappingCurrencyRow(
          1,
          "poe",
          1,
          1,
          "current",
          "Metadata/Wrong",
          "Known")
      ]);

    await Assert.ThrowsAsync<InvalidOperationException>(
      () => fixture.Worker.RunIteration(CancellationToken.None));
    fixture.Repository.Verify(
      repository => repository.Apply(
        It.IsAny<IReadOnlyList<GameMappingReport>>(),
        It.IsAny<IReadOnlyList<ConfirmedAlias>>()),
      Times.Never);
  }

  [Fact]
  public async Task TransactionFailureIsSurfaced()
  {
    var fixture = new WorkerFixture(applyChanges: true);
    fixture.Repository.Setup(repository => repository.Apply(
        It.IsAny<IReadOnlyList<GameMappingReport>>(),
        It.IsAny<IReadOnlyList<ConfirmedAlias>>()))
      .ThrowsAsync(new InvalidOperationException("transaction failed"));

    var exception = await Assert.ThrowsAsync<InvalidOperationException>(
      () => fixture.Worker.RunIteration(CancellationToken.None));

    Assert.Equal("transaction failed", exception.Message);
  }

  private sealed class WorkerFixture
  {
    public Mock<IGameRepository> Games { get; } = new();
    public Mock<IRealmRepository> Realms { get; } = new();
    public Mock<ICurrencyItemMappingRepository> Repository { get; } = new();
    public Mock<IMappingFeedClient> Feeds { get; } = new();
    public CurrencyItemMappingWorker Worker { get; }

    public WorkerFixture(bool applyChanges)
    {
      var configuration = new ConfigurationBuilder()
        .AddInMemoryCollection(new Dictionary<string, string?>
        {
          ["DbConnectionString"] = "Host=test",
          ["ApplyChanges"] = applyChanges.ToString()
        })
        .Build();
      var config = BaseConfig.FromConfig<CurrencyItemMappingConfig>(configuration);

      Games.Setup(repository => repository.GetGames())
        .ReturnsAsync([new Game(1, "poe", "Path of Exile", "trade", 1)]);
      Realms.Setup(repository => repository.GetRealms())
        .ReturnsAsync([new Realm(1, 1, "pc")]);
      Repository.Setup(repository => repository.GetCurrencies())
        .ReturnsAsync([
          new MappingCurrencyRow(1, "poe", 1, 1, "current", null, "Known")
        ]);
      Repository.Setup(repository => repository.Apply(
          It.IsAny<IReadOnlyList<GameMappingReport>>(),
          It.IsAny<IReadOnlyList<ConfirmedAlias>>()))
        .Returns(Task.CompletedTask);
      Feeds.Setup(client => client.GetBaseItems("poe", It.IsAny<CancellationToken>()))
        .ReturnsAsync([new BaseItemCandidate("Metadata/Known", "Known")]);
      Feeds.Setup(client => client.GetCurrentTradeApiIds(
          "trade",
          It.IsAny<CancellationToken>()))
        .ReturnsAsync(new HashSet<string>(["current"], StringComparer.Ordinal));
      Feeds.Setup(client => client.GetCdnBaseItemTypeIds(
          It.IsAny<IReadOnlyList<Realm>>(),
          It.IsAny<int>(),
          It.IsAny<CancellationToken>()))
        .ReturnsAsync(new HashSet<string>(["Metadata/Known"], StringComparer.Ordinal));

      Worker = new CurrencyItemMappingWorker(
        config,
        Games.Object,
        Realms.Object,
        Repository.Object,
        Feeds.Object,
        new CurrencyMappingPlanner(),
        new CurrencyItemMappingDiagnostics(
          NullLogger<CurrencyItemMappingDiagnostics>.Instance),
        (_, _) => Task.CompletedTask);
    }
  }
}
