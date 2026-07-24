namespace Poe2scout.Repositories.League.Models;

public record League(
  int LeagueId,
  string Value,
  string ShortName,
  int BaseCurrencyItemId,
  string? BaseCurrencyApiId,
  string? BaseCurrencyBaseItemTypeId,
  string BaseCurrencyText,
  string? BaseCurrencyIconUrl,
  bool CurrentLeague);
