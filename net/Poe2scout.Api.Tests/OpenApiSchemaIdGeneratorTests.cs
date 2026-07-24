using System.Text.Json;
using CurrencyGetByCategoryResponse =
  Poe2scout.Api.Handlers.Currencies.GetByCategoryHandler.GetByCategoryResponse;
using UniqueGetByCategoryResponse =
  Poe2scout.Api.Handlers.Uniques.GetByCategoryHandler.GetByCategoryResponse;
using Xunit;

namespace Poe2scout.Api.Tests;

public sealed class OpenApiSchemaIdGeneratorTests
{
  [Fact]
  public void CreateUsesFinalNamespacePartAndModelName()
  {
    var currencySchemaId = OpenApiSchemaIdGenerator.Create(
      JsonSerializerOptions.Default.GetTypeInfo(typeof(CurrencyGetByCategoryResponse)));
    var uniqueSchemaId = OpenApiSchemaIdGenerator.Create(
      JsonSerializerOptions.Default.GetTypeInfo(typeof(UniqueGetByCategoryResponse)));

    Assert.Equal("Currencies.GetByCategoryResponse", currencySchemaId);
    Assert.Equal("Uniques.GetByCategoryResponse", uniqueSchemaId);
  }

  [Fact]
  public void CreatePreservesDefaultInliningBehavior()
  {
    var schemaId = OpenApiSchemaIdGenerator.Create(
      JsonSerializerOptions.Default.GetTypeInfo(typeof(string)));

    Assert.Null(schemaId);
  }
}
