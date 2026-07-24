namespace Poe2scout.CurrencyItemMapping.Worker;

public sealed class CurrencyItemMappingDiagnostics(
  ILogger<CurrencyItemMappingDiagnostics> logger)
{
  public void RecordReport(GameMappingReport report, bool applyChanges)
  {
    logger.LogInformation(
      "Currency mapping {mode} for {game}: mapped={mapped}, unchanged={unchanged}, missing={missing}, ambiguous={ambiguous}, duplicate={duplicate}, unknown_cdn={unknownCdn}",
      applyChanges ? "apply" : "dry-run",
      report.GameApiId,
      report.Mapped,
      report.Unchanged,
      report.Missing,
      report.Ambiguous,
      report.Duplicate,
      report.UnknownCdnBaseItemTypeIds.Count);

    foreach (var issue in report.Issues)
    {
      logger.LogWarning(
        "Currency mapping {kind} for {game}:{currency}: {detail}",
        issue.Kind,
        report.GameApiId,
        issue.Currency,
        issue.Detail);
    }

    if (report.UnknownCdnBaseItemTypeIds.Count > 0)
    {
      logger.LogWarning(
        "Unknown CDN base item IDs for {game}: {identifiers}",
        report.GameApiId,
        string.Join(", ", report.UnknownCdnBaseItemTypeIds));
    }
  }

  public void RecordAliases(IReadOnlyList<ConfirmedAlias> aliases, bool applyChanges)
  {
    foreach (var alias in aliases)
    {
      logger.LogInformation(
        "{mode} confirmed alias {game}:{retired} -> {canonical}",
        applyChanges ? "Applying" : "Would apply",
        alias.GameApiId,
        alias.RetiredApiId,
        alias.CanonicalApiId);
    }
  }

  public void RecordFailure(Exception exception)
  {
    logger.LogError(exception, "Currency item mapping iteration failed closed.");
  }

  public void RecordApplied(
    IReadOnlyList<GameMappingReport> reports,
    IReadOnlyList<ConfirmedAlias> aliases)
  {
    logger.LogInformation(
      "Committed currency mapping transaction: mappings={mappings}, aliases={aliases}",
      reports.Sum(report => report.Mapped),
      aliases.Count);
  }
}
