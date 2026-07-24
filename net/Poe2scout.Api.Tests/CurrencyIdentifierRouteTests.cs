using System.Text.Encodings.Web;
using Poe2scout.Api.Handlers.Currencies;
using Xunit;

namespace Poe2scout.Api.Tests;

public sealed class CurrencyIdentifierRouteTests
{
  [Theory]
  [InlineData("chaos", "chaos")]
  [InlineData(
    "Metadata%2FItems%2FCurrency%2FCurrencyRerollRare",
    "Metadata/Items/Currency/CurrencyRerollRare")]
  public void DecodesLegacyAndBaseItemIdentifiers(
    string routeValue,
    string expected)
  {
    Assert.Equal(expected, Uri.UnescapeDataString(routeValue));
  }
}
