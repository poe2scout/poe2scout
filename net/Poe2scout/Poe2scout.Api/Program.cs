using OpenTelemetry.Logs;
using Poe2scout;
using Poe2scout.Api;
using Poe2scout.Api.Ioc;
using Poe2scout.Repositories;

var builder = WebApplication.CreateBuilder(args);
var apiConfig = BaseConfig.FromConfig<ApiConfig>(builder.Configuration);

builder.Services.AddSingleton(apiConfig);
builder.Services.AddOpenApi();
builder.Services.ConfigureHttpJsonOptions(options =>
{
  options.SerializerOptions.PropertyNamingPolicy = null;
});
builder.Services.AddCors(options =>
{
  options.AddDefaultPolicy(policy =>
    policy
      .WithOrigins(
        "https://poe2scout.com",
        "https://api.poe2scout.com")
      .AllowAnyHeader()
      .AllowAnyMethod());
});
builder.Services.AddDataSource(apiConfig.DbConnectionString);
builder.Services.AddPoe2scoutRepositories();
builder.Services.AddSingleton<EconomyCache>();
builder.Services.AddSingleton<ItemsCache>();
builder.Services.AddScoutMetrics(apiConfig);
builder.Logging.AddOpenTelemetry(logging =>
{
  logging.AddOtlpExporter(options => options.ApplyGrafanaOptions(apiConfig, "logs"));
});
var app = builder.Build();

app.UseCors();
app.UseMiddleware<ApiDiagnosticsMiddleware>();
app.MapOpenApi();
app.UseSwaggerUI(options =>
{
  options.SwaggerEndpoint("/openapi/v1.json", "My API v1");
});
app.MapHandlers();
app.UseRateLimiter();
app.Run();
