using System.Text.Json;
using Poe2scout.Api.Handlers.Currencies;
using Poe2scout.Api.Handlers.Leagues;
using Xunit;

namespace Poe2scout.Api.Tests;

public sealed class CurrencyIdentifierSerializationTests
{
  private static readonly JsonSerializerOptions JsonOptions =
    new(JsonSerializerDefaults.Web);

  [Fact]
  public void CurrencyResponseSerializesNullableLegacyAndBaseIdentifiers()
  {
    var response = new Poe2scout.Api.Handlers.Currencies.GetHandler.GetResponse(
      CurrencyItemId: 1,
      ItemId: 2,
      CurrencyCategoryId: 3,
      ApiId: null,
      BaseItemTypeId: "Metadata/Items/Currency/Test",
      Text: "Test Currency",
      CategoryApiId: "currency",
      IconUrl: null,
      ItemMetadata: null,
      PriceLogs: [],
      CurrentPrice: null);

    using var json = JsonDocument.Parse(JsonSerializer.Serialize(response, JsonOptions));

    Assert.Equal(JsonValueKind.Null, json.RootElement.GetProperty("apiId").ValueKind);
    Assert.Equal(
      "Metadata/Items/Currency/Test",
      json.RootElement.GetProperty("baseItemTypeId").GetString());
  }

  [Fact]
  public void ExchangeResponseSerializesBothBaseCurrencyIdentifierFields()
  {
    var response = new GetExchangeSnapshotHandler.GetExchangeSnapshotResponse(
      Epoch: 123,
      Volume: 1,
      MarketCap: 2,
      BaseCurrencyApiId: null,
      BaseCurrencyBaseItemTypeId: "Metadata/Items/Currency/Base",
      BaseCurrencyText: "Base");

    using var json = JsonDocument.Parse(JsonSerializer.Serialize(response, JsonOptions));

    Assert.Equal(
      JsonValueKind.Null,
      json.RootElement.GetProperty("baseCurrencyApiId").ValueKind);
    Assert.Equal(
      "Metadata/Items/Currency/Base",
      json.RootElement.GetProperty("baseCurrencyBaseItemTypeId").GetString());
  }
}
