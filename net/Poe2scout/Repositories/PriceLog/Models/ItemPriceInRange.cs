namespace Poe2scout.Repositories.PriceLog.Models;

public record ItemPriceInRange(
  int ItemId,
  decimal Price,
  decimal Quantity);
