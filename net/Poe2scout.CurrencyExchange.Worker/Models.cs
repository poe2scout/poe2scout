using System.Text.Json.Serialization;

namespace Poe2scout.CurrencyExchange.Worker;

public sealed record TradingPair(
  [property: JsonPropertyName("league")] string League,
  [property: JsonPropertyName("market_id")] string MarketId,
  [property: JsonPropertyName("market_pair")] List<string> MarketPair,
  [property: JsonPropertyName("volume_traded")] Dictionary<string, int> VolumeTraded,
  [property: JsonPropertyName("highest_stock")] Dictionary<string, int> HighestStock);

public sealed record CurrencyExchangeResponse(
  [property: JsonPropertyName("next_change_id")] int NextChangeId,
  [property: JsonPropertyName("markets")] List<TradingPair> Markets);
