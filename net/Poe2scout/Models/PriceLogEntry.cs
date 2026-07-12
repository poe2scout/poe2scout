namespace Poe2scout.Models;

public record PriceLogEntry(
  double Price,
  DateTime Time,
  int Quantity);
