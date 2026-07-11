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
      "implicitMods": ["Adds 1 to [Fire|Fire] Damage"],
      "explicitMods": ["Damage-10"],
      "extended": {
        "mods": {
          "implicit": [{"magnitudes":[{"min":"1","max":"2"}]}],
          "explicit": [{"magnitudes":[{"min":"10","max":"20"}]}]
        },
        "hashes": {
          "implicit": [["hash",[0]]],
          "explicit": [["hash",[0]]]
        }
      }
    }
    """);

    var metadata = UniqueItemMetadataExtractor.Extract(document.RootElement);

    Assert.Equal("Description [one|display]", metadata["description"] as string);
    Assert.Equal("first\nsecond", metadata["flavor_text"] as string);
    Assert.Equal("20", ((Dictionary<string, object>)metadata["properties"])["Quality"]);
    Assert.Equal("64", ((Dictionary<string, object>)metadata["requirements"])["Level"]);
    Assert.Equal("Adds (1-2) to Fire Damage", Assert.Single((List<string>)metadata["implicit_mods"]));
    Assert.Equal("Damage(10-20)", Assert.Single((List<string>)metadata["explicit_mods"]));
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
