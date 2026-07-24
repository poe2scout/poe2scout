using Poe2scout;
using Poe2scout.CurrencyItemMapping.Worker;
using Poe2scout.Repositories;

var builder = Host.CreateApplicationBuilder(args);
var config = BaseConfig.FromConfig<CurrencyItemMappingConfig>(builder.Configuration);

builder.Services.AddSingleton(config);
builder.Services.AddDataSource(config.DbConnectionString);
builder.Services.AddPoe2scoutRepositories();
builder.Services.AddSingleton<ICurrencyItemMappingRepository, CurrencyItemMappingRepository>();
builder.Services.AddSingleton<CurrencyMappingPlanner>();
builder.Services.AddSingleton<CurrencyItemMappingDiagnostics>();
builder.Services
  .AddHttpClient<IMappingFeedClient, MappingFeedClient>()
  .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
  {
    PooledConnectionLifetime = TimeSpan.FromMinutes(15)
  });
builder.Services.AddHostedService<CurrencyItemMappingWorker>();

await builder.Build().RunAsync();
