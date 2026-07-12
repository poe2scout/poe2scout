namespace Poe2scout.ItemSync.Worker;

public sealed class ItemFeedResponse
{
  public List<ItemFeedCategory>? Result { get; init; }
}

public sealed class ItemFeedCategory
{
  public string? Id { get; init; }
  public string? Label { get; init; }
  public List<ItemFeedEntry>? Entries { get; init; }
}

public sealed class ItemFeedEntry
{
  public string? Type { get; init; }
  public string? Name { get; init; }
  public string? Text { get; init; }
}

public sealed class CurrencyFeedResponse
{
  public List<CurrencyFeedCategory>? Result { get; init; }
}

public sealed class CurrencyFeedCategory
{
  public string? Id { get; set; }
  public string? Label { get; init; }
  public List<CurrencyFeedEntry>? Entries { get; init; }
}

public sealed class CurrencyFeedEntry
{
  public string? Id { get; init; }
  public string? Image { get; init; }
  public string? Text { get; init; }
}
