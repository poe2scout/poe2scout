namespace Poe2scout.Models;

public record UniqueItem(
  int UniqueItemId,
  int ItemId,
  string? IconUrl,
  string Text,
  string Name,
  string CategoryApiId,
  Dictionary<string, object>? ItemMetadata,
  string Type,
  bool? IsChanceable,
  bool IsCurrent);
