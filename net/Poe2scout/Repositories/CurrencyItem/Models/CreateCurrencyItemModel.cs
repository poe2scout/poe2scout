namespace Poe2scout.Repositories.CurrencyItem.Models;

public record CreateCurrencyItemModel(
  int ItemId,
  int ItemCategoryId,
  string? ApiId,
  string? BaseItemTypeId,
  string Text,
  string? Image);
