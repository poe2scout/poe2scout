using Microsoft.OpenApi;
using Xunit;

namespace Poe2scout.Api.Tests;

public sealed class RequireAllSchemaPropertiesTransformerTests
{
  [Fact]
  public void ApplyMarksEveryDeclaredPropertyAsRequiredWithoutChangingItsSchema()
  {
    var nullableProperty = new OpenApiSchema
    {
      Type = JsonSchemaType.String | JsonSchemaType.Null
    };
    var schema = new OpenApiSchema
    {
      Properties = new Dictionary<string, IOpenApiSchema>
      {
        ["AlwaysPresent"] = new OpenApiSchema
        {
          Type = JsonSchemaType.Integer
        },
        ["NullableButPresent"] = nullableProperty
      }
    };

    RequireAllSchemaPropertiesTransformer.Apply(schema);

    Assert.NotNull(schema.Required);
    Assert.Equal(
      ["AlwaysPresent", "NullableButPresent"],
      schema.Required.OrderBy(property => property));
    Assert.Equal(JsonSchemaType.String | JsonSchemaType.Null, nullableProperty.Type);
  }
}
