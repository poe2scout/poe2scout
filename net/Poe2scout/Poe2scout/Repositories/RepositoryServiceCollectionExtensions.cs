using System.Data.Common;
using Microsoft.Extensions.DependencyInjection;
using Npgsql;
using Poe2scout.Repositories.CurrencyExchange;
using Poe2scout.Repositories.CurrencyItem;
using Poe2scout.Repositories.Game;
using Poe2scout.Repositories.Item;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.PriceLog;
using Poe2scout.Repositories.Realm;
using Poe2scout.Repositories.Service;
using Poe2scout.Repositories.UniqueItem;

namespace Poe2scout.Repositories;

public static class RepositoryServiceCollectionExtensions
{
  public static IServiceCollection AddDataSource(this IServiceCollection services, string connectionString)
  {
    services.AddSingleton<DbDataSource>(_ => NpgsqlDataSource.Create(connectionString));
    
    return services;
  }
  
  public static IServiceCollection AddPoe2scoutRepositories(this IServiceCollection services)
  {
    services.AddSingleton<ICurrencyExchangeRepository, CurrencyExchangeRepository>();
    services.AddSingleton<ICurrencyItemRepository, CurrencyItemRepository>();
    services.AddSingleton<IGameRepository, GameRepository>();
    services.AddSingleton<IItemRepository, ItemRepository>();
    services.AddSingleton<ILeagueRepository, LeagueRepository>();
    services.AddSingleton<IPriceLogRepository, PriceLogRepository>();
    services.AddSingleton<IRealmRepository, RealmRepository>();
    services.AddSingleton<IServiceRepository, ServiceRepository>();
    services.AddSingleton<IUniqueItemRepository, UniqueItemRepository>();

    return services;
  }
}
