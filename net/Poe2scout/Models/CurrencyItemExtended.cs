namespace Poe2scout.Models;

public record CurrencyItemExtended(
  int CurrencyItemId,
  int ItemId,
  int CurrencyCategoryId,
  string? ApiId,
  string? BaseItemTypeId,
  string Text,
  string CategoryApiId,
  string? IconUrl,
  Dictionary<string, object>? ItemMetadata,
  IReadOnlyList<PriceLogEntry?> PriceLogs,
  double? CurrentPrice,
  int? CurrentQuantity) : CurrencyItem(
    CurrencyItemId,
    ItemId,
    CurrencyCategoryId,
    ApiId,
    BaseItemTypeId,
    Text,
    CategoryApiId,
    IconUrl,
    ItemMetadata);
