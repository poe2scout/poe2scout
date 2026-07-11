using Poe2scout;
using Poe2scout.Repositories;
using Poe2scout.UniquePriceLog.Worker;

var builder = Host.CreateApplicationBuilder(args);
var config = BaseConfig.FromConfig<UniquePriceLogConfig>(builder.Configuration);

builder.Services.AddSingleton(config);
builder.Services.AddDataSource(config.DbConnectionString);
builder.Services.AddPoe2scoutRepositories();
builder.Services
  .AddHttpClient<IPoeTradeClient, PoeTradeClient>()
  .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
  {
    PooledConnectionLifetime = TimeSpan.FromMinutes(15)
  });
builder.Services.AddHostedService<UniquePriceLogWorker>();

await builder.Build().RunAsync();
