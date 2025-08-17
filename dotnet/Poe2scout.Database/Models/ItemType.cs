namespace Poe2scout.Database.Models;

public class ItemType(
    int itemTypeId, 
    string name, 
    int itemCategoryId)
{
    public int ItemTypeId { get; } = itemTypeId;
    public string Name { get; } = name;
    public int ItemCategoryId { get; } = itemCategoryId;
}