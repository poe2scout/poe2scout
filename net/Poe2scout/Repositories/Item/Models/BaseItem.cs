namespace Poe2scout.Repositories.Item.Models;

public record BaseItem(
  int BaseItemId,
  int ItemTypeId,
  int GameId,
  string? IconUrl,
  Dictionary<string, object>? ItemMetadata);
