using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Poe2scout.Api;

public class UtcDateTimeJsonConverter : JsonConverter<DateTime>
{
  public override DateTime Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
  {
    return DateTime.Parse(reader.GetString()!, CultureInfo.InvariantCulture).ToUniversalTime();
  }

  public override void Write(Utf8JsonWriter writer, DateTime value, JsonSerializerOptions options)
  {
    writer.WriteStringValue(value.ToUniversalTime().ToString("O"));
  }
}
