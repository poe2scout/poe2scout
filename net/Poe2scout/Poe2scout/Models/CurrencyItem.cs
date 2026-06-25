namespace Poe2scout.Models;

public class CurrencyItem(
  int currencyItemId,
  int itemId,
  int currencyCategoryId,
  string apiId,
  string text,
  string categoryApiId,
  string? iconUrl,
  Dictionary<string, string>? itemMetadata)
{
  public int CurrencyItemId { get; } = currencyItemId;
  public int ItemId { get; } = itemId;
  public int CurrencyCategoryId { get; } = currencyCategoryId;
  public string ApiId { get; } = apiId;
  public string Text { get; } = text;
  public string CategoryApiId { get; } = categoryApiId;
  public string? IconUrl { get; } = iconUrl;
  public Dictionary<string, string>? ItemMetadata { get; } = itemMetadata;
}