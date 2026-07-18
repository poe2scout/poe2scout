using System.Text.Json;
using System.Text.RegularExpressions;

namespace Poe2scout.UniquePriceLog.Worker;

internal static class UniqueItemMetadataExtractor
{
  public static Dictionary<string, object> Extract(JsonElement item)
  {
    var metadata = new Dictionary<string, object>
    {
      ["name"] = StringProperty(item, "name")!,
      ["base_type"] = StringProperty(item, "baseType")!,
      ["item_level"] = NumberProperty(item, "ilvl")!,
      ["icon"] = StringProperty(item, "icon")!,
      ["properties"] = new Dictionary<string, object>(),
      ["implicit_mods"] = new List<string>(),
      ["explicit_mods"] = new List<string>(),
      ["flavor_text"] = JoinStringArray(item, "flavourText")!,
      ["requirements"] = new Dictionary<string, object>(),
      ["description"] = StringProperty(item, "descrText")!
    };

    var properties = (Dictionary<string, object>)metadata["properties"];
    if (TryGetArray(item, "properties", out var propertyValues))
    {
      foreach (var property in propertyValues.EnumerateArray())
      {
        var name = CleanPropertyName(StringProperty(property, "name") ?? string.Empty);
        var value = FirstNestedValue(property, "values");
        properties[name] = value is null ? null! : value.Contains('|') ? value.Split('|').Last() : value;
      }
    }

    var requirements = (Dictionary<string, object>)metadata["requirements"];
    if (TryGetArray(item, "requirements", out var requirementValues))
    {
      foreach (var requirement in requirementValues.EnumerateArray())
      {
        var name = StringProperty(requirement, "name") ?? string.Empty;
        if (name.Contains('|'))
        {
          name = name.Split('|').Last().TrimEnd(']').TrimStart('[');
        }

        var value = FirstNestedValue(requirement, "values");
        if (value is not null)
        {
          requirements[name] = value;
        }
      }
    }

    if ((StringProperty(item, "baseType") ?? string.Empty).Contains("Relic", StringComparison.Ordinal))
    {
      requirements["Level"] = "64";
    }

    var implicitMods = (List<string>)metadata["implicit_mods"];
    var explicitMods = (List<string>)metadata["explicit_mods"];
    var implicitRanges = new Dictionary<int, ModRange>();
    var explicitRanges = new Dictionary<int, ModRange>();
    PopulateRanges(item, implicitRanges, explicitRanges);

    if (TryGetArray(item, "implicitMods", out var implicitValues))
    {
      var index = 0;
      foreach (var mod in implicitValues.EnumerateArray())
      {
        var cleanMod = CleanBracketText(mod.GetString() ?? string.Empty);
        if (implicitRanges.TryGetValue(index, out var range))
        {
          cleanMod = AddRange(cleanMod, range, new Regex(@"\d+"));
        }

        implicitMods.Add(cleanMod);
        index++;
      }
    }

    if (TryGetArray(item, "explicitMods", out var explicitValues))
    {
      var index = 0;
      foreach (var mod in explicitValues.EnumerateArray())
      {
        var cleanMod = CleanBracketText(mod.ValueKind == JsonValueKind.Object
          ? StringProperty(mod, "description") ?? string.Empty
          : mod.GetString() ?? string.Empty);
        ModRange? range = null;
        var isEmbeddedRange = false;
        if (TryGetEmbeddedRange(mod, out var embeddedRange))
        {
          range = embeddedRange;
          isEmbeddedRange = true;
        }
        else if (explicitRanges.TryGetValue(index, out var extendedRange))
        {
          range = extendedRange;
        }

        if (range is not null
            && (isEmbeddedRange
              ? range.Min != range.Max
              : !(range.Min == "1" && range.Max == "1")))
        {
          cleanMod = AddRange(cleanMod, range, new Regex(@"-?\d+"), trimDash: true);
        }

        explicitMods.Add(cleanMod);
        index++;
      }
    }

    return metadata;
  }

  private static void PopulateRanges(
    JsonElement item,
    Dictionary<int, ModRange> implicitRanges,
    Dictionary<int, ModRange> explicitRanges)
  {
    if (!TryGetObject(item, "extended", out var extended)
        || !TryGetObject(extended, "mods", out var mods)
        || !TryGetObject(extended, "hashes", out var hashes))
    {
      return;
    }

    if (TryGetArray(mods, "sanctum", out var sanctumMods))
    {
      if (TryGetArray(hashes, "sanctum", out var sanctumHashes))
      {
        PopulateRangeMap(sanctumMods, sanctumHashes, explicitRanges);
      }

      return;
    }

    if (TryGetArray(mods, "implicit", out var implicitMods)
        && TryGetArray(hashes, "implicit", out var implicitHashes))
    {
      PopulateRangeMap(implicitMods, implicitHashes, implicitRanges);
    }

    if (TryGetArray(mods, "explicit", out var explicitMods)
        && TryGetArray(hashes, "explicit", out var explicitHashes))
    {
      PopulateRangeMap(explicitMods, explicitHashes, explicitRanges);
    }
  }

  private static bool TryGetEmbeddedRange(JsonElement mod, out ModRange range)
  {
    range = null!;
    if (mod.ValueKind != JsonValueKind.Object
        || !TryGetArray(mod, "mods", out var mods))
    {
      return false;
    }

    foreach (var nestedMod in mods.EnumerateArray())
    {
      if (!TryGetArray(nestedMod, "magnitudes", out var magnitudes))
      {
        continue;
      }

      foreach (var magnitude in magnitudes.EnumerateArray())
      {
        var min = StringProperty(magnitude, "min");
        var max = StringProperty(magnitude, "max");
        if (min is not null && max is not null)
        {
          range = new ModRange(min, max);
          return true;
        }
      }
    }

    return false;
  }

  private static void PopulateRangeMap(
    JsonElement mods,
    JsonElement hashes,
    Dictionary<int, ModRange> ranges)
  {
    var hashIndex = 0;
    foreach (var hash in hashes.EnumerateArray())
    {
      if (GetHashModIndex(hash) is int modIndex
          && modIndex < mods.GetArrayLength()
          && mods[modIndex].ValueKind == JsonValueKind.Object
          && TryGetArray(mods[modIndex], "magnitudes", out var magnitudes))
      {
        foreach (var magnitude in magnitudes.EnumerateArray())
        {
          var min = StringProperty(magnitude, "min");
          var max = StringProperty(magnitude, "max");
          if (min is not null && max is not null)
          {
            ranges[hashIndex] = new ModRange(min, max);
          }
        }
      }

      hashIndex++;
    }
  }

  private static int? GetHashModIndex(JsonElement hash)
  {
    if (hash.ValueKind != JsonValueKind.Array || hash.GetArrayLength() < 2)
    {
      return null;
    }

    var targets = hash[1];
    if (targets.ValueKind != JsonValueKind.Array || targets.GetArrayLength() == 0)
    {
      return null;
    }

    return targets[0].ValueKind == JsonValueKind.Number && targets[0].TryGetInt32(out var index)
      ? index
      : null;
  }

  private static string AddRange(string mod, ModRange range, Regex numberPattern, bool trimDash = false)
  {
    var match = numberPattern.Match(mod);
    if (!match.Success)
    {
      return mod;
    }

    var prefix = mod[..match.Index];
    if (trimDash)
    {
      prefix = prefix.TrimEnd('-');
    }

    return $"{prefix}({range.Min}-{range.Max}){mod[(match.Index + match.Length)..]}";
  }

  private static string CleanPropertyName(string value)
  {
    var cleanName = value.Replace("[", string.Empty).Replace("]", string.Empty);
    if (cleanName.Contains('|'))
    {
      cleanName = cleanName.Split('|').Last();
    }

    return cleanName.Replace(":", string.Empty).Trim();
  }

  internal static string CleanBracketText(string value)
  {
    while (value.Contains('[') && value.Contains(']'))
    {
      var start = value.IndexOf('[');
      var end = value.IndexOf(']', start + 1);
      var formatted = value[(start + 1)..end].Split('|').Last();
      value = value[..start] + formatted + value[(end + 1)..];
    }

    return value;
  }

  internal static string? StringProperty(JsonElement element, string name)
  {
    if (!element.TryGetProperty(name, out var value) || value.ValueKind == JsonValueKind.Null)
    {
      return null;
    }

    return value.ValueKind == JsonValueKind.String ? value.GetString() : value.GetRawText();
  }

  private static object? NumberProperty(JsonElement element, string name)
  {
    if (!element.TryGetProperty(name, out var value) || value.ValueKind == JsonValueKind.Null)
    {
      return null;
    }

    if (value.ValueKind == JsonValueKind.Number && value.TryGetInt64(out var integer))
    {
      return integer;
    }

    return ElementText(value);
  }

  private static string? JoinStringArray(JsonElement element, string name)
    => TryGetArray(element, name, out var values)
      && values.GetArrayLength() > 0
      ? string.Join("\n", values.EnumerateArray().Select(value => value.GetString() ?? string.Empty))
      : null;

  private static string? FirstNestedValue(JsonElement element, string name)
  {
    if (!TryGetArray(element, name, out var values)
        || values.GetArrayLength() == 0
        || values[0].ValueKind != JsonValueKind.Array
        || values[0].GetArrayLength() == 0)
    {
      return null;
    }

    return ElementText(values[0][0]);
  }

  private static string? ElementText(JsonElement element)
    => element.ValueKind switch
    {
      JsonValueKind.String => element.GetString(),
      JsonValueKind.Number => element.GetRawText(),
      JsonValueKind.True => "true",
      JsonValueKind.False => "false",
      _ => null
    };

  private static bool TryGetObject(JsonElement element, string name, out JsonElement value)
    => element.TryGetProperty(name, out value) && value.ValueKind == JsonValueKind.Object;

  private static bool TryGetArray(JsonElement element, string name, out JsonElement value)
    => element.TryGetProperty(name, out value) && value.ValueKind == JsonValueKind.Array;

  private sealed record ModRange(string Min, string Max);
}

internal static class CurrencyItemMetadataExtractor
{
  public static Dictionary<string, object> Extract(JsonElement item)
  {
    var effects = new List<string>();
    if (TryGetArray(item, "explicitMods", out var explicitMods))
    {
      effects.AddRange(explicitMods.EnumerateArray()
        .Select(mod => UniqueItemMetadataExtractor.CleanBracketText(mod.GetString() ?? string.Empty)));
    }

    var secondaryDescription = UniqueItemMetadataExtractor.StringProperty(item, "secDescrText");
    if (!string.IsNullOrEmpty(secondaryDescription))
    {
      effects.Clear();
      effects.Add(UniqueItemMetadataExtractor.CleanBracketText(secondaryDescription));
    }

    var description = UniqueItemMetadataExtractor.StringProperty(item, "descrText");
    return new Dictionary<string, object>
    {
      ["name"] = UniqueItemMetadataExtractor.StringProperty(item, "typeLine")!,
      ["base_type"] = UniqueItemMetadataExtractor.StringProperty(item, "baseType")!,
      ["icon"] = UniqueItemMetadataExtractor.StringProperty(item, "icon")!,
      ["stack_size"] = 1,
      ["max_stack_size"] = NumberProperty(item, "maxStackSize")!,
      ["description"] = description is null
        ? null!
        : UniqueItemMetadataExtractor.CleanBracketText(description),
      ["effect"] = effects
    };
  }

  private static object? NumberProperty(JsonElement element, string name)
  {
    if (!element.TryGetProperty(name, out var value) || value.ValueKind == JsonValueKind.Null)
    {
      return null;
    }

    return value.ValueKind == JsonValueKind.Number && value.TryGetInt64(out var integer)
      ? integer
      : value.GetRawText();
  }

  private static bool TryGetArray(JsonElement element, string name, out JsonElement value)
    => element.TryGetProperty(name, out value) && value.ValueKind == JsonValueKind.Array;
}
