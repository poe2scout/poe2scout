namespace Poe2scout.Repositories.Game.Models;

public record BridgeCurrency(
  int ItemId,
  int CurrencyItemId,
  string ApiId,
  string Text,
  string? IconUrl,
  int BridgeRank);
