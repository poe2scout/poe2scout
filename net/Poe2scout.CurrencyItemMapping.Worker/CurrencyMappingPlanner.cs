namespace Poe2scout.CurrencyItemMapping.Worker;

public sealed class CurrencyMappingPlanner
{
  public GameMappingReport BuildPlan(
    int gameId,
    string gameApiId,
    IReadOnlyList<MappingCurrencyRow> currencies,
    IReadOnlyList<BaseItemCandidate> baseItems,
    IReadOnlySet<string> currentTradeApiIds,
    IReadOnlySet<string> cdnBaseItemTypeIds)
  {
    var issues = new List<MappingIssue>();
    var assignments = new List<MappingAssignment>();
    var missing = 0;
    var ambiguous = 0;
    var duplicate = 0;
    var duplicateBaseIds = new HashSet<string>(StringComparer.Ordinal);

    var existingMappings = currencies
      .Where(currency => currency.BaseItemTypeId is not null)
      .GroupBy(currency => currency.BaseItemTypeId!, StringComparer.Ordinal);
    foreach (var mapping in existingMappings.Where(group => group.Count() > 1))
    {
      duplicate++;
      duplicateBaseIds.Add(mapping.Key);
      issues.Add(new MappingIssue(
        "duplicate",
        mapping.Key,
        $"Existing mapping is assigned to: {string.Join(", ", mapping.Select(row => row.ApiId ?? row.Text))}"));
    }

    var candidatesByName = baseItems
      .GroupBy(candidate => candidate.Name, StringComparer.Ordinal)
      .ToDictionary(group => group.Key, group => group.ToList(), StringComparer.Ordinal);

    foreach (var currency in currencies.OrderBy(row => row.CurrencyItemId))
    {
      if (currency.ApiId is null || !currentTradeApiIds.Contains(currency.ApiId))
      {
        continue;
      }

      if (currency.ApiId == "loyalty-tattoo-of-ikiahoCopy")
      {
        if (currency.BaseItemTypeId is not null)
        {
          issues.Add(new MappingIssue(
            "duplicate",
            currency.ApiId,
            "The retained Copy row must remain legacy-ID-only."));
          duplicate++;
        }

        continue;
      }

      if (!candidatesByName.TryGetValue(currency.Text, out var candidates))
      {
        missing++;
        issues.Add(new MappingIssue("missing", currency.ApiId, currency.Text));
        continue;
      }

      BaseItemCandidate? selected = candidates.Count == 1 ? candidates[0] : null;
      if (selected is null)
      {
        var sampledCandidates = candidates
          .Where(candidate => cdnBaseItemTypeIds.Contains(candidate.BaseItemTypeId))
          .ToList();
        if (sampledCandidates.Count == 1)
        {
          selected = sampledCandidates[0];
        }
      }

      if (selected is null)
      {
        ambiguous++;
        issues.Add(new MappingIssue(
          "ambiguous",
          currency.ApiId,
          string.Join(", ", candidates.Select(candidate => candidate.BaseItemTypeId))));
        continue;
      }

      if (currency.BaseItemTypeId is not null
          && !string.Equals(
            currency.BaseItemTypeId,
            selected.BaseItemTypeId,
            StringComparison.Ordinal))
      {
        duplicate++;
        issues.Add(new MappingIssue(
          "duplicate",
          currency.ApiId,
          $"Existing base ID {currency.BaseItemTypeId} conflicts with proposed {selected.BaseItemTypeId}."));
        continue;
      }

      assignments.Add(new MappingAssignment(
        currency.CurrencyItemId,
        currency.ApiId,
        selected.BaseItemTypeId,
        currency.BaseItemTypeId is not null));
    }

    foreach (var collision in assignments
               .GroupBy(assignment => assignment.BaseItemTypeId, StringComparer.Ordinal)
               .Where(group => group.Count() > 1))
    {
      duplicate++;
      duplicateBaseIds.Add(collision.Key);
      issues.Add(new MappingIssue(
        "duplicate",
        collision.Key,
        $"Proposed for: {string.Join(", ", collision.Select(assignment => assignment.ApiId))}"));
    }

    var assignmentsByCurrencyItemId = assignments.ToDictionary(
      assignment => assignment.CurrencyItemId);
    var futureMappings = currencies
      .Select(currency => new
      {
        Currency = currency,
        BaseItemTypeId = assignmentsByCurrencyItemId.TryGetValue(
          currency.CurrencyItemId,
          out var assignment)
          ? assignment.BaseItemTypeId
          : currency.BaseItemTypeId
      })
      .Where(mapping => mapping.BaseItemTypeId is not null)
      .GroupBy(mapping => mapping.BaseItemTypeId!, StringComparer.Ordinal);
    foreach (var collision in futureMappings.Where(group => group.Count() > 1))
    {
      if (!duplicateBaseIds.Add(collision.Key))
      {
        continue;
      }

      duplicate++;
      issues.Add(new MappingIssue(
        "duplicate",
        collision.Key,
        $"Would be assigned to: {string.Join(", ", collision.Select(mapping => mapping.Currency.ApiId ?? mapping.Currency.Text))}"));
    }

    assignments.RemoveAll(
      assignment => duplicateBaseIds.Contains(assignment.BaseItemTypeId));

    var knownBaseIds = currencies
      .Where(currency => currency.BaseItemTypeId is not null)
      .Select(currency => currency.BaseItemTypeId!)
      .Concat(assignments.Select(assignment => assignment.BaseItemTypeId))
      .ToHashSet(StringComparer.Ordinal);
    var unknownCdnIds = cdnBaseItemTypeIds
      .Where(identifier => !knownBaseIds.Contains(identifier))
      .Order(StringComparer.Ordinal)
      .ToList();

    return new GameMappingReport(
      gameId,
      gameApiId,
      assignments,
      issues,
      assignments.Count(assignment => !assignment.IsUnchanged),
      assignments.Count(assignment => assignment.IsUnchanged),
      missing,
      ambiguous,
      duplicate,
      unknownCdnIds);
  }
}
