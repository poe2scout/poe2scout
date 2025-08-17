namespace Poe2scout.Database.Models;

public class ItemCategory(
    int itemCategoryId, 
    string apiId, 
    string label)
{
    public int ItemCategoryId { get; } = itemCategoryId;
    public string ApiId { get; } = apiId;
    public string Label { get; } = label;
}