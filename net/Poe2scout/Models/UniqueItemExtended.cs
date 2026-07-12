namespace Poe2scout.Models;

public record UniqueItemExtended(
  int UniqueItemId,
  int ItemId,
  string? IconUrl,
  string Text,
  string Name,
  string CategoryApiId,
  Dictionary<string, object>? ItemMetadata,
  string Type,
  bool? IsChanceable,
  bool IsCurrent,
  IReadOnlyList<PriceLogEntry?> PriceLogs,
  double? CurrentPrice,
  int? CurrentQuantity) : UniqueItem(
    UniqueItemId,
    ItemId,
    IconUrl,
    Text,
    Name,
    CategoryApiId,
    ItemMetadata,
    Type,
    IsChanceable,
    IsCurrent);
