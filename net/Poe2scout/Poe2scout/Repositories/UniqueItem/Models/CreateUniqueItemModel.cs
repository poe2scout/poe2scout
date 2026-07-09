namespace Poe2scout.Repositories.UniqueItem.Models;

public record CreateUniqueItemModel(
  int ItemId,
  string? IconUrl,
  string Text,
  string Name);
