namespace Poe2scout.Database.Models;

public class CurrencyItem(
    int itemId,
    string apiId,
    string text,
    string currencyCategoryApiId,
    string? iconUrl,
    string itemMetaData,
    string itemTypeName)
{
    public string ApiId { get; } = apiId;
    public string Text { get; } = text;
    public string CurrencyCategoryApiId { get; } = currencyCategoryApiId;
    public string? IconUrl { get; } = iconUrl;
    public string ItemMetaData { get; } = itemMetaData;
    public Item Item { get; } = new(itemTypeName, itemId);
}