using Poe2scout;
using Poe2scout.CurrencyPriceLog.Worker;
using Poe2scout.Repositories;

var builder = Host.CreateApplicationBuilder(args);
var config = BaseConfig.FromConfig<CurrencyPriceLogConfig>(builder.Configuration);

builder.Services.AddSingleton(config);
builder.Services.AddDataSource(config.DbConnectionString);
builder.Services.AddPoe2scoutRepositories();
builder.Services
  .AddHttpClient<IPoeCurrencyExchangeClient, PoeCurrencyExchangeClient>()
  .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
  {
    PooledConnectionLifetime = TimeSpan.FromMinutes(15)
  });
builder.Services.AddHostedService<CurrencyPriceLogWorker>();

await builder.Build().RunAsync();
