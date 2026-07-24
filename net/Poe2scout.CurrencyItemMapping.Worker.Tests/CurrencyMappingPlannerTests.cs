namespace Poe2scout.CurrencyItemMapping.Worker.Tests;

public sealed class CurrencyMappingPlannerTests
{
  private readonly CurrencyMappingPlanner planner = new();

  [Fact]
  public void MapsUniqueExactOrdinalName()
  {
    var report = Plan(
      [Currency("current", "Chaos Orb")],
      [Base("Metadata/Items/Currency/Chaos", "Chaos Orb")],
      ["current"],
      []);

    var assignment = Assert.Single(report.Assignments);
    Assert.Equal("Metadata/Items/Currency/Chaos", assignment.BaseItemTypeId);
    Assert.Equal(1, report.Mapped);
    Assert.Equal(0, report.Ambiguous);
  }

  [Fact]
  public void ResolvesDuplicateNameOnlyWhenExactlyOneCandidateIsInCdnSample()
  {
    var report = Plan(
      [Currency("current", "Invitation")],
      [
        Base("Metadata/Items/Invitation/A", "Invitation"),
        Base("Metadata/Items/Invitation/B", "Invitation")
      ],
      ["current"],
      ["Metadata/Items/Invitation/B"]);

    Assert.Equal(
      "Metadata/Items/Invitation/B",
      Assert.Single(report.Assignments).BaseItemTypeId);
  }

  [Fact]
  public void ReportsMissingAndUnresolvedAmbiguousNames()
  {
    var report = Plan(
      [
        Currency("missing", "Missing"),
        Currency("ambiguous", "Duplicate", currencyItemId: 2)
      ],
      [
        Base("Metadata/A", "Duplicate"),
        Base("Metadata/B", "Duplicate")
      ],
      ["missing", "ambiguous"],
      ["Metadata/A", "Metadata/B"]);

    Assert.Empty(report.Assignments);
    Assert.Equal(1, report.Missing);
    Assert.Equal(1, report.Ambiguous);
  }

  [Fact]
  public void IgnoresStaleLegacyAlias()
  {
    var report = Plan(
      [
        Currency("retired-id", "Renamed"),
        Currency("current-id", "Renamed", currencyItemId: 2)
      ],
      [Base("Metadata/Renamed", "Renamed")],
      ["current-id"],
      ["Metadata/Renamed"]);

    Assert.Equal("current-id", Assert.Single(report.Assignments).ApiId);
  }

  [Fact]
  public void KeepsTattooCopyLegacyOnlyAndMapsCanonicalRow()
  {
    var report = Plan(
      [
        Currency("loyalty-tattoo-of-ikiaho", "Loyalty Tattoo of Ikiaho"),
        Currency(
          "loyalty-tattoo-of-ikiahoCopy",
          "Loyalty Tattoo of Ikiaho",
          currencyItemId: 2)
      ],
      [Base("Metadata/Items/Tattoos/Ikiaho", "Loyalty Tattoo of Ikiaho")],
      ["loyalty-tattoo-of-ikiaho", "loyalty-tattoo-of-ikiahoCopy"],
      ["Metadata/Items/Tattoos/Ikiaho"]);

    Assert.Equal(
      "loyalty-tattoo-of-ikiaho",
      Assert.Single(report.Assignments).ApiId);
  }

  [Fact]
  public void ReportsUnknownCdnIdentifiersWithoutCreatingAssignments()
  {
    var report = Plan(
      [Currency("current", "Known")],
      [Base("Metadata/Known", "Known")],
      ["current"],
      ["Metadata/Known", "Metadata/Unknown"]);

    Assert.Equal(["Metadata/Unknown"], report.UnknownCdnBaseItemTypeIds);
  }

  [Fact]
  public void RepeatedPlanMarksExistingMappingUnchanged()
  {
    var report = Plan(
      [Currency("current", "Known", baseItemTypeId: "Metadata/Known")],
      [Base("Metadata/Known", "Known")],
      ["current"],
      ["Metadata/Known"]);

    Assert.True(Assert.Single(report.Assignments).IsUnchanged);
    Assert.Equal(0, report.Mapped);
    Assert.Equal(1, report.Unchanged);
  }

  [Fact]
  public void ConflictingExistingMappingFailsClosed()
  {
    var report = Plan(
      [Currency("current", "Known", baseItemTypeId: "Metadata/Wrong")],
      [Base("Metadata/Known", "Known")],
      ["current"],
      ["Metadata/Known"]);

    Assert.Empty(report.Assignments);
    Assert.Equal(1, report.Duplicate);
  }

  [Fact]
  public void ProposedMappingCollidingWithAnotherExistingRowFailsClosed()
  {
    var report = Plan(
      [
        Currency(
          "already-mapped",
          "Existing",
          currencyItemId: 1,
          baseItemTypeId: "Metadata/Shared"),
        Currency("new-row", "New", currencyItemId: 2)
      ],
      [
        Base("Metadata/Shared", "Existing"),
        Base("Metadata/Shared", "New")
      ],
      ["already-mapped", "new-row"],
      ["Metadata/Shared"]);

    Assert.Empty(report.Assignments);
    Assert.Equal(1, report.Duplicate);
  }

  private GameMappingReport Plan(
    IReadOnlyList<MappingCurrencyRow> currencies,
    IReadOnlyList<BaseItemCandidate> candidates,
    string[] currentTradeIds,
    string[] cdnIds)
    => planner.BuildPlan(
      1,
      "poe",
      currencies,
      candidates,
      currentTradeIds.ToHashSet(StringComparer.Ordinal),
      cdnIds.ToHashSet(StringComparer.Ordinal));

  private static MappingCurrencyRow Currency(
    string apiId,
    string text,
    int currencyItemId = 1,
    string? baseItemTypeId = null)
    => new(1, "poe", currencyItemId, currencyItemId, apiId, baseItemTypeId, text);

  private static BaseItemCandidate Base(string identifier, string name)
    => new(identifier, name);
}
