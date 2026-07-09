namespace Poe2scout.Repositories.PriceLog.Models;

public record RecordPriceModel(
  int ItemId,
  int LeagueId,
  double Price,
  int Quantity,
  int RealmId);
