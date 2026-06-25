using System.Data;
using System.Text.Json;
using Dapper;

namespace Poe2scout.Repositories;

internal sealed class DictionaryJsonTypeHandler : SqlMapper.TypeHandler<Dictionary<string, object>>
{
  public override Dictionary<string, object> Parse(object value)
  {
    if (value is Dictionary<string, object> dictionary)
    {
      return dictionary;
    }

    if (value is JsonDocument document)
    {
      return ConvertObject(document.RootElement);
    }

    return ConvertObject(JsonDocument.Parse(value.ToString() ?? "{}").RootElement);
  }

  public override void SetValue(IDbDataParameter parameter, Dictionary<string, object>? value)
  {
    parameter.Value = value is null ? DBNull.Value : JsonSerializer.Serialize(value);
  }

  private static Dictionary<string, object> ConvertObject(JsonElement element)
  {
    var dictionary = new Dictionary<string, object>();
    foreach (var property in element.EnumerateObject())
    {
      dictionary[property.Name] = ConvertElement(property.Value)!;
    }

    return dictionary;
  }

  private static object? ConvertElement(JsonElement element)
    => element.ValueKind switch
    {
      JsonValueKind.Object => ConvertObject(element),
      JsonValueKind.Array => element.EnumerateArray().Select(ConvertElement).ToList(),
      JsonValueKind.String => element.GetString(),
      JsonValueKind.Number when element.TryGetInt64(out var longValue) => longValue,
      JsonValueKind.Number when element.TryGetDouble(out var doubleValue) => doubleValue,
      JsonValueKind.True => true,
      JsonValueKind.False => false,
      _ => null
    };
}