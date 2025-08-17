namespace Poe2scout.Database.Models;

public class PriceLog(float price, DateTime timeUtc, int quantity)
{
    public float Price { get; } = price;
    public DateTime TimeUtc { get; } = timeUtc;
    public int Quantity { get; } = quantity;
}