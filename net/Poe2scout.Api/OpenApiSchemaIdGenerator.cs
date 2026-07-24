using System.Text.Json.Serialization.Metadata;
using Microsoft.AspNetCore.OpenApi;

namespace Poe2scout.Api;

internal static class OpenApiSchemaIdGenerator
{
  public static string? Create(JsonTypeInfo jsonTypeInfo)
  {
    if (OpenApiOptions.CreateDefaultSchemaReferenceId(jsonTypeInfo) is null)
    {
      return null;
    }

    var modelType = jsonTypeInfo.Type;
    var modelNamespace = modelType.Namespace;
    if (string.IsNullOrEmpty(modelNamespace))
    {
      return modelType.Name;
    }

    var finalNamespaceSeparator = modelNamespace.LastIndexOf('.');
    var finalNamespacePart = modelNamespace[(finalNamespaceSeparator + 1)..];

    return $"{finalNamespacePart}.{modelType.Name}";
  }
}
