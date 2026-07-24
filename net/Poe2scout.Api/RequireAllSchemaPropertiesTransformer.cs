using Microsoft.AspNetCore.OpenApi;
using Microsoft.OpenApi;

namespace Poe2scout.Api;

internal sealed class RequireAllSchemaPropertiesTransformer : IOpenApiSchemaTransformer
{
  public Task TransformAsync(
    OpenApiSchema schema,
    OpenApiSchemaTransformerContext context,
    CancellationToken cancellationToken)
  {
    Apply(schema);

    return Task.CompletedTask;
  }

  internal static void Apply(OpenApiSchema schema)
  {
    if (schema.Properties is null || schema.Properties.Count == 0)
    {
      return;
    }

    schema.Required ??= new HashSet<string>(StringComparer.Ordinal);
    schema.Required.UnionWith(schema.Properties.Keys);
  }
}
