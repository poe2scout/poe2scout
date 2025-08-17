namespace Poe2scout.Database.Models;

public class UniqueItem(
    int itemId,
    string? iconUrl,
    string name,
    string text,
    string itemMetadata,
    bool isChanceable,
    string categoryApiId,
    string itemTypeName)
{
    public string? IconUrl { get; } = iconUrl;
    public string Text { get; } = text;
    public string Name { get; } = name;
    public string ItemMetadata { get; } = itemMetadata;
    public bool IsChanceable { get; } = isChanceable;
    public string CategoryApiId { get; } = categoryApiId;
    public Item Item { get; } = new(itemTypeName, itemId);
}