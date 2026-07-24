using Poe2scout.Repositories.Game;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.CurrencyItemMapping.Worker;

public sealed class CurrencyItemMappingWorker(
  CurrencyItemMappingConfig config,
  IGameRepository gameRepository,
  IRealmRepository realmRepository,
  ICurrencyItemMappingRepository mappingRepository,
  IMappingFeedClient feedClient,
  CurrencyMappingPlanner planner,
  CurrencyItemMappingDiagnostics diagnostics,
  Func<TimeSpan, CancellationToken, Task>? delay = null) : BackgroundService
{
  private static readonly IReadOnlyList<ConfirmedAlias> ConfirmedAliases =
  [
    new("poe2", "abyss-key", "kulemaks-invitation"),
    new("poe2", "essence-of-abyss", "essence-of-the-abyss"),
    new("poe2", "omen-of-abyssal-favours", "omen-of-abyssal-echoes"),
    new("poe2", "rite-of-passage", "azmeri-reliquary-key"),
    new("poe2", "serpent-idol", "snake-idol"),
    new("poe", "blessing-general", "flesh-of-xesht")
  ];

  protected override async Task ExecuteAsync(CancellationToken stoppingToken)
  {
    while (!stoppingToken.IsCancellationRequested)
    {
      try
      {
        await RunIteration(stoppingToken);
      }
      catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
      {
        return;
      }
      catch (Exception exception)
      {
        diagnostics.RecordFailure(exception);

        throw;
      }

      await Delay(TimeSpan.FromMinutes(config.PollIntervalMinutes), stoppingToken);
    }
  }

  public async Task<IReadOnlyList<GameMappingReport>> RunIteration(
    CancellationToken cancellationToken)
  {
    var games = await gameRepository.GetGames();
    var realms = await realmRepository.GetRealms();
    var currencies = await mappingRepository.GetCurrencies();
    var lastCompletedHour = (int)(DateTimeOffset.UtcNow.ToUnixTimeSeconds() / 3600 * 3600 - 3600);
    var reports = new List<GameMappingReport>();

    foreach (var game in games.OrderBy(game => game.GameId))
    {
      var gameRows = currencies.Where(row => row.GameId == game.GameId).ToList();

      ValidateAliases(game.ApiId, gameRows);

      var gameRealms = realms.Where(realm => realm.GameId == game.GameId).ToList();
      var baseItemsTask = feedClient.GetBaseItems(game.ApiId, cancellationToken);
      var tradeIdsTask = feedClient.GetCurrentTradeApiIds(
        game.GggApiTradeIdentifier,
        cancellationToken);
      var cdnIdsTask = feedClient.GetCdnBaseItemTypeIds(
        gameRealms,
        lastCompletedHour,
        cancellationToken);
      await Task.WhenAll(baseItemsTask, tradeIdsTask, cdnIdsTask);

      var report = planner.BuildPlan(
        game.GameId,
        game.ApiId,
        gameRows,
        await baseItemsTask,
        await tradeIdsTask,
        await cdnIdsTask);
      diagnostics.RecordReport(report, config.ApplyChanges);
      reports.Add(report);
    }

    var aliasesToMerge = GetAliasesToMerge(currencies);
    diagnostics.RecordAliases(aliasesToMerge, config.ApplyChanges);

    if (reports.Any(report => report.Duplicate > 0))
    {
      throw new InvalidOperationException(
        "Mapping conflicts were found. No currency mappings or aliases were changed.");
    }

    if (config.ApplyChanges)
    {
      await mappingRepository.Apply(reports, aliasesToMerge);
      diagnostics.RecordApplied(reports, aliasesToMerge);
    }

    return reports;
  }

  private static void ValidateAliases(
    string gameApiId,
    IReadOnlyList<MappingCurrencyRow> currencies)
  {
    foreach (var alias in ConfirmedAliases.Where(alias => alias.GameApiId == gameApiId))
    {
      var retired = currencies.SingleOrDefault(row => row.ApiId == alias.RetiredApiId);
      if (retired is null)
      {
        continue;
      }

      if (currencies.SingleOrDefault(row => row.ApiId == alias.CanonicalApiId) is null)
      {
        throw new InvalidOperationException(
          $"Confirmed alias target {gameApiId}:{alias.CanonicalApiId} is missing.");
      }
    }
  }

  private static IReadOnlyList<ConfirmedAlias> GetAliasesToMerge(
    IReadOnlyList<MappingCurrencyRow> currencies)
  {
    var rowsByGameAndApiId = currencies
      .Where(row => row.ApiId is not null)
      .ToDictionary(row => (row.GameApiId, row.ApiId!), row => row);
    return ConfirmedAliases
      .Where(alias => rowsByGameAndApiId.ContainsKey((alias.GameApiId, alias.RetiredApiId)))
      .ToList();
  }

  private Task Delay(TimeSpan duration, CancellationToken cancellationToken)
    => delay is null ? Task.Delay(duration, cancellationToken) : delay(duration, cancellationToken);
}
