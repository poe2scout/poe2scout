namespace Poe2scout.Database.Models;

public class BaseItem(
    int baseItemId, 
    int itemTypeId,
    string itemTypeName,
    int itemTypeCategoryId,
    string? iconUrl, 
    IDictionary<object, object>? itemMetaData)
{
    public int BaseItemId { get; } = baseItemId;
    public string? IconUrl { get; } = iconUrl;
    public IDictionary<object, object>? ItemMetaData { get; } = itemMetaData;
    public ItemType ItemType { get; } = new(itemTypeId, itemTypeName, itemTypeCategoryId);
}