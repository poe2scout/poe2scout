using Poe2scout;
using Poe2scout.Api;
using Poe2scout.Api.Ioc;
using Poe2scout.Repositories;

var builder = WebApplication.CreateBuilder(args);
var apiConfig = BaseConfig.FromConfig<ApiConfig>(builder.Configuration);

builder.Services.AddSingleton(apiConfig);
builder.Services.AddOpenApi();
builder.Services.AddDataSource(apiConfig.DbConnectionString);
builder.Services.AddPoe2scoutRepositories();
builder.Services.AddSingleton<EconomyCache>();
builder.Services.AddSingleton<ItemsCache>();
builder.Services.AddScoutMetrics(apiConfig);
builder.Services.AddScoutRateLimiting();

var app = builder.Build();

app.MapOpenApi();
app.MapHandlers();
app.UseRateLimiter();
app.Run();

