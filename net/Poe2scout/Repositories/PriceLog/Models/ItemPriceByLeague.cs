namespace Poe2scout.Repositories.PriceLog.Models;

public record ItemPriceByLeague(
  int LeagueId,
  int ItemId,
  double Price);
