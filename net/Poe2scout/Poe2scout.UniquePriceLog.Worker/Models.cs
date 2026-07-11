using System.Text.Json;
using System.Text.Json.Serialization;
using Poe2scout.Models;

namespace Poe2scout.UniquePriceLog.Worker;

public sealed record PriceFetchResult(double Price, int Quantity, string Currency);

public sealed record TradeSearchResponse(
  [property: JsonPropertyName("id")] string Id,
  [property: JsonPropertyName("result")] List<string> Result,
  [property: JsonPropertyName("total")] int Total);

public sealed record TradeFetchResponse(
  [property: JsonPropertyName("result")] List<TradeResult?> Result);

public sealed record TradeResult(
  [property: JsonPropertyName("listing")] TradeListing? Listing,
  [property: JsonPropertyName("item")] JsonElement? Item);

public sealed record TradeListing(
  [property: JsonPropertyName("price")] TradePrice? Price);

public sealed record TradePrice(
  [property: JsonPropertyName("amount")] JsonElement Amount);
