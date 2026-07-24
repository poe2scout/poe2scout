namespace Poe2scout.Models;

public record CurrencyItem(
  int CurrencyItemId,
  int ItemId,
  int CurrencyCategoryId,
  string? ApiId,
  string? BaseItemTypeId,
  string Text,
  string CategoryApiId,
  string? IconUrl,
  Dictionary<string, object>? ItemMetadata);
