namespace Poe2scout.Repositories.Game.Models;

public record Game(
  int GameId,
  string ApiId,
  string Label,
  string GggApiTradeIdentifier,
  int DefaultLeagueId);
