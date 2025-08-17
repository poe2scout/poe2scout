namespace Poe2scout.Database.Models;

public class Item(string name, int itemId)
{
    public string Name { get; } = name;
    public int ItemId { get; } = itemId;
}