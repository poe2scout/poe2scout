using Microsoft.Extensions.Configuration;
using System.ComponentModel;
using System.Globalization;
using System.Reflection;

namespace Poe2scout;

public class BaseConfig
{
  public static TConfig FromConfig<TConfig>(IConfiguration configuration)
    where TConfig : BaseConfig, new()
  {
    ArgumentNullException.ThrowIfNull(configuration);

    var config = new TConfig();
    BindProperties(config, configuration);
    return config;
  }

  private static void BindProperties(object target, IConfiguration configuration)
  {
    foreach (var property in target.GetType().GetProperties(BindingFlags.Instance | BindingFlags.Public))
    {
      if (property.SetMethod is null)
      {
        continue;
      }

      var section = configuration.GetSection(property.Name);
      var rawValue = section.Value;

      if (rawValue is not null)
      {
        property.SetValue(target, ConvertValue(rawValue, property.PropertyType));
        continue;
      }

      if (!section.GetChildren().Any() || IsScalarType(property.PropertyType))
      {
        continue;
      }

      var nestedTargetType = Nullable.GetUnderlyingType(property.PropertyType) ?? property.PropertyType;
      var nestedTarget = property.GetValue(target) ?? Activator.CreateInstance(nestedTargetType);

      if (nestedTarget is null)
      {
        throw new InvalidOperationException($"Could not create an instance of {nestedTargetType.FullName}.");
      }

      BindProperties(nestedTarget, section);
      property.SetValue(target, nestedTarget);
    }
  }

  private static bool IsScalarType(Type type)
  {
    var targetType = Nullable.GetUnderlyingType(type) ?? type;

    return targetType.IsPrimitive ||
           targetType.IsEnum ||
           targetType == typeof(string) ||
           targetType == typeof(decimal) ||
           targetType == typeof(DateTime) ||
           targetType == typeof(DateTimeOffset) ||
           targetType == typeof(TimeSpan) ||
           targetType == typeof(Guid);
  }

  private static object? ConvertValue(string value, Type type)
  {
    var targetType = Nullable.GetUnderlyingType(type) ?? type;

    if (targetType == typeof(string))
    {
      return value;
    }

    if (targetType.IsEnum)
    {
      return Enum.Parse(targetType, value, ignoreCase: true);
    }

    var converter = TypeDescriptor.GetConverter(targetType);

    if (converter.CanConvertFrom(typeof(string)))
    {
      return converter.ConvertFromInvariantString(value);
    }

    return Convert.ChangeType(value, targetType, CultureInfo.InvariantCulture);
  }
}
