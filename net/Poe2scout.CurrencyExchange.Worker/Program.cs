using Poe2scout;
using Poe2scout.CurrencyExchange.Worker;
using Poe2scout.Repositories;

var builder = Host.CreateApplicationBuilder(args);
var config = BaseConfig.FromConfig<CurrencyExchangeConfig>(builder.Configuration);

builder.Services.AddSingleton(config);
builder.Services.AddDataSource(config.DbConnectionString);
builder.Services.AddPoe2scoutRepositories();
builder.Services
  .AddHttpClient<ICurrencyExchangeClient, PoeCurrencyExchangeClient>()
  .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
  {
    PooledConnectionLifetime = TimeSpan.FromMinutes(15)
  });
builder.Services.AddHostedService<CurrencyExchangeWorker>();

await builder.Build().RunAsync();
