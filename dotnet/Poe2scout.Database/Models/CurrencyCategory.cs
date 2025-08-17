namespace Poe2scout.Database.Models;

public class CurrencyCategory(int currencyCategoryId, string apiId, string label)
{
    public int CurrencyCategoryId { get; } = currencyCategoryId;
    public string ApiId { get; } = apiId;
    public string Label { get; } = label;
}