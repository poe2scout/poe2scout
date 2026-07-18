using System.Text.Json;
using Poe2scout.UniquePriceLog.Worker;

namespace Poe2scout.UniquePriceLog.Worker.Tests;

public class MetadataExtractorTests
{
  [Fact]
  public void ExtractsUniqueMetadataAndModRanges()
  {
    using var document = JsonDocument.Parse("""
    {
      "name": "Test Relic",
      "baseType": "Test Relic",
      "ilvl": 86,
      "icon": "icon-url",
      "flavourText": ["first", "second"],
      "descrText": "Description [one|display]",
      "properties": [{"name":"[Quality]|Quality:","values":[["20"]]}],
      "requirements": [{"name":"[Level]|Level]","values":[["70"]]}],
      "implicitMods": ["+14 to [Strength|Strength]"],
      "explicitMods": [{
          "description":"10% increased maximum Life",
          "hash":"stat.explicit.stat_983749596",
          "mods":[{
            "magnitudes":[{"min":"10","max":"20"}]
            }]
        },
        {
          "description":"+56% to [Resistances|Fire Resistance]",
          "hash":"stat.explicit.stat_3372524247",
          "mods":[{
            "magnitudes":[{"min":"50","max":"100"}]
            }]
        },
        {
          "description":"Enemies in your [Presence] have -25% to Fire Resistance",
          "hash":"stat.explicit.stat_990363519",
          "mods":[{
            "level":66,
            "magnitudes":[{"min":"-25","max":"-25"}]
            }]
        }],
      "extended": {
        "mods": {
          "implicit": [{"name":"","tier":"","level":10,"magnitudes":[{"hash":"implicit.stat_4080418644","min":"10","max":"15"}]}]
        },
        "hashes": {
          "implicit": [["implicit.stat_4080418644",[0]]],
          "explicit": [["explicit.stat_983749596",[0]],["explicit.stat_3372524247",[2]],["explicit.stat_990363519",[1]]]
        }
      }
    }
    """);

    var metadata = UniqueItemMetadataExtractor.Extract(document.RootElement);

    Assert.Equal("Description [one|display]", metadata["description"] as string);
    Assert.Equal("first\nsecond", metadata["flavor_text"] as string);
    Assert.Equal("20", ((Dictionary<string, object>)metadata["properties"])["Quality"]);
    Assert.Equal("64", ((Dictionary<string, object>)metadata["requirements"])["Level"]);
    Assert.Equal("+(10-15) to Strength", Assert.Single((List<string>)metadata["implicit_mods"]));
    Assert.Equal([
      "(10-20)% increased maximum Life",
      "+(50-100)% to Fire Resistance",
      "Enemies in your Presence have -25% to Fire Resistance"
    ], (List<string>)metadata["explicit_mods"]);
  }

  [Fact]
  public void ExtractsCurrencyEffectsAndSecondaryDescription()
  {
    using var document = JsonDocument.Parse("""
    {
      "typeLine": "Test Orb",
      "baseType": "Test Orb",
      "icon": "icon-url",
      "maxStackSize": 20,
      "descrText": "Description [one|display]",
      "explicitMods": ["Effect [one|display]"] ,
      "secDescrText": "Secondary [one|display]"
    }
    """);

    var metadata = CurrencyItemMetadataExtractor.Extract(document.RootElement);

    Assert.Equal("Description display", metadata["description"] as string);
    Assert.Equal(20L, metadata["max_stack_size"]);
    Assert.Equal(["Secondary display"], (List<string>)metadata["effect"]);
  }
}
