using System.Net;
using System.Text;
using Microsoft.Extensions.Configuration;
using Poe2scout.Repositories.Realm.Models;

namespace Poe2scout.CurrencyItemMapping.Worker.Tests;

public sealed class MappingFeedClientTests
{
  [Fact]
  public async Task LoadsCorrectRePoePathAndSkipsExpectedUnnamedEntries()
  {
    var handler = new RecordingHandler(_ => Json("""
      {
        "Metadata/Named": { "name": "Named Currency" },
        "Metadata/Unnamed": { "name": null }
      }
      """));
    var client = CreateClient(handler);

    var items = await client.GetBaseItems("poe2", CancellationToken.None);

    Assert.Equal("Metadata/Named", Assert.Single(items).BaseItemTypeId);
    Assert.Equal(
      "https://repoe-fork.github.io/poe2/base_items.json",
      Assert.Single(handler.Requests));
  }

  [Fact]
  public async Task LoadsCurrentTradeStaticIdentifiers()
  {
    var handler = new RecordingHandler(_ => Json("""
      {
        "result": [
          {
            "id": "Currency",
            "entries": [
              { "id": "chaos", "text": "Chaos Orb" },
              { "id": "sep", "text": "" },
              { "id": "divine", "text": "Divine Orb" }
            ]
          },
          {
            "id": "MapKey",
            "entries": [
              { "id": "map-tier-1", "text": "Map (Tier 1)" }
            ]
          }
        ]
      }
      """));
    var client = CreateClient(handler);

    var identifiers = await client.GetCurrentTradeApiIds(
      "poe2",
      CancellationToken.None);

    Assert.Equal(["chaos", "divine"], identifiers.Order(StringComparer.Ordinal));
    Assert.DoesNotContain("map-tier-1", identifiers);
    Assert.Equal(
      "https://www.pathofexile.com/api/poe2/data/static",
      Assert.Single(handler.Requests));
  }

  [Fact]
  public async Task UnionsEveryRealmCdnMarketPair()
  {
    var handler = new RecordingHandler(request =>
      request.RequestUri!.AbsolutePath.Contains("/xbox/")
        ? Json(Snapshot("Metadata/Xbox", "Metadata/Common"))
        : Json(Snapshot("Metadata/Pc", "Metadata/Common")));
    var client = CreateClient(handler);

    var identifiers = await client.GetCdnBaseItemTypeIds(
      [new Realm(1, 1, "pc"), new Realm(2, 1, "xbox")],
      123,
      CancellationToken.None);

    Assert.Equal(
      ["Metadata/Common", "Metadata/Pc", "Metadata/Xbox"],
      identifiers.Order(StringComparer.Ordinal));
    Assert.Contains(
      "https://web.poecdn.com/api/currency-exchange/123",
      handler.Requests);
    Assert.Contains(
      "https://web.poecdn.com/api/currency-exchange/xbox/123",
      handler.Requests);
  }

  private static MappingFeedClient CreateClient(RecordingHandler handler)
  {
    var configuration = new ConfigurationBuilder().Build();
    var config = BaseConfig.FromConfig<CurrencyItemMappingConfig>(configuration);
    return new MappingFeedClient(new HttpClient(handler), config);
  }

  private static HttpResponseMessage Json(string json)
    => new(HttpStatusCode.OK)
    {
      Content = new StringContent(json, Encoding.UTF8, "application/json")
    };

  private static string Snapshot(string first, string second)
    => $$"""
      {
        "next_change_id": 124,
        "markets": [{ "market_pair": ["{{first}}", "{{second}}"] }]
      }
      """;

  private sealed class RecordingHandler(
    Func<HttpRequestMessage, HttpResponseMessage> responseFactory) : HttpMessageHandler
  {
    private readonly object sync = new();
    public List<string> Requests { get; } = [];

    protected override Task<HttpResponseMessage> SendAsync(
      HttpRequestMessage request,
      CancellationToken cancellationToken)
    {
      lock (sync)
      {
        Requests.Add(request.RequestUri!.ToString());
      }

      return Task.FromResult(responseFactory(request));
    }
  }
}
