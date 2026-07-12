using Poe2scout;
using Poe2scout.ItemSync.Worker;
using Poe2scout.Repositories;

var builder = Host.CreateApplicationBuilder(args);
var config = BaseConfig.FromConfig<ItemSyncConfig>(builder.Configuration);

builder.Services.AddSingleton(config);
builder.Services.AddDataSource(config.DbConnectionString);
builder.Services.AddPoe2scoutRepositories();
builder.Services
  .AddHttpClient<IItemSyncClient, ItemSyncClient>()
  .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
  {
    PooledConnectionLifetime = TimeSpan.FromMinutes(15)
  });
builder.Services.AddHostedService<ItemSyncWorker>();

await builder.Build().RunAsync();
