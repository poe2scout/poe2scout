namespace Poe2scout.Models;

public record CurrencyItemWithBaseId(
  int CurrencyItemId,
  int ItemId,
  int CurrencyCategoryId,
  string BaseItemTypeId,
  string Text,
  string CategoryApiId,
  string? IconUrl,
  Dictionary<string, object>? ItemMetadata);