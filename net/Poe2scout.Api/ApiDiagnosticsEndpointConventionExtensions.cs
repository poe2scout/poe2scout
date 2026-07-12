namespace Poe2scout.Api;

public sealed class ExcludeFromApiDiagnosticsMetadata
{
  public static readonly ExcludeFromApiDiagnosticsMetadata Instance = new();

  private ExcludeFromApiDiagnosticsMetadata()
  {
  }
}

public static class ApiDiagnosticsEndpointConventionExtensions
{
  public static TBuilder ExcludeFromApiDiagnostics<TBuilder>(this TBuilder builder)
    where TBuilder : IEndpointConventionBuilder
  {
    builder.Add(endpointBuilder =>
      endpointBuilder.Metadata.Add(ExcludeFromApiDiagnosticsMetadata.Instance));
    return builder;
  }
}
