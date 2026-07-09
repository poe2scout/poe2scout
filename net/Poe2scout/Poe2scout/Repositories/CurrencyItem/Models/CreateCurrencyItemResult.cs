namespace Poe2scout.Repositories.CurrencyItem.Models;

public record CreateCurrencyItemResult(
  bool Ok,
  int? CurrencyItemId,
  CreateCurrencyItemError? Error);
