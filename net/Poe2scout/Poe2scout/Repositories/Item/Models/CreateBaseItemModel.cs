namespace Poe2scout.Repositories.Item.Models;

public record CreateBaseItemModel(
  int GameId,
  int ItemTypeId,
  string? IconUrl,
  Dictionary<string, object>? ItemMetadata);
