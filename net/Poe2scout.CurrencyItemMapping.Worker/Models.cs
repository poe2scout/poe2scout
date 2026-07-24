using System.Text.Json.Serialization;

namespace Poe2scout.CurrencyItemMapping.Worker;

public sealed record MappingCurrencyRow(
  int GameId,
  string GameApiId,
  int CurrencyItemId,
  int ItemId,
  string? ApiId,
  string? BaseItemTypeId,
  string Text);

public sealed record BaseItemCandidate(string BaseItemTypeId, string Name);

public sealed record MappingAssignment(
  int CurrencyItemId,
  string ApiId,
  string BaseItemTypeId,
  bool IsUnchanged);

public sealed record MappingIssue(string Kind, string Currency, string Detail);

public sealed record GameMappingReport(
  int GameId,
  string GameApiId,
  IReadOnlyList<MappingAssignment> Assignments,
  IReadOnlyList<MappingIssue> Issues,
  int Mapped,
  int Unchanged,
  int Missing,
  int Ambiguous,
  int Duplicate,
  IReadOnlyList<string> UnknownCdnBaseItemTypeIds);

public sealed record ConfirmedAlias(string GameApiId, string RetiredApiId, string CanonicalApiId);

public sealed record TradeStaticResponse(
  [property: JsonPropertyName("result")] List<TradeStaticCategory>? Result);

public sealed record TradeStaticCategory(
  [property: JsonPropertyName("id")] string? Id,
  [property: JsonPropertyName("entries")] List<TradeStaticEntry>? Entries);

public sealed record TradeStaticEntry(
  [property: JsonPropertyName("id")] string? Id,
  [property: JsonPropertyName("text")] string? Text);

public sealed record CdnExchangeResponse(
  [property: JsonPropertyName("next_change_id")] int NextChangeId,
  [property: JsonPropertyName("markets")] List<CdnMarket>? Markets);

public sealed record CdnMarket(
  [property: JsonPropertyName("market_pair")] List<string> MarketPair);
