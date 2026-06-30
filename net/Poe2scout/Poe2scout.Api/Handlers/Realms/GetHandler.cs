using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Poe2scout.Repositories.Game;
using Poe2scout.Repositories.League;
using Poe2scout.Repositories.Realm;

namespace Poe2scout.Api.Handlers.Realms;

public static class GetHandler
{
  public static async Task<Ok<List<GetResponse>>> Get(
    [FromServices] IGameRepository gameRepository,
    [FromServices] IRealmRepository realmRepository,
    [FromServices] ILeagueRepository leagueRepository)
  {
    var games = await gameRepository.GetGames();
    var realms = await realmRepository.GetRealms();

    var gameLookup = games.ToDictionary(game => game.GameId);
    var defaultLeagueLookup = new Dictionary<int, string>();

    foreach (var game in games)
    {
      var defaultLeague = await leagueRepository.GetLeague(game.DefaultLeagueId);
      defaultLeagueLookup[game.GameId] = defaultLeague.Value;
    }

    var response = realms
      .OrderBy(realm => GetGameSortOrder(gameLookup[realm.GameId].ApiId))
      .ThenBy(realm => GetRealmSortOrder(realm.ApiId))
      .Select(realm =>
      {
        var game = gameLookup[realm.GameId];
        var gameDisplay = GetGameDisplay(game.ApiId);
        var value = $"{gameDisplay}/{realm.ApiId}";

        return new GetResponse(
          value,
          value,
          game.ApiId,
          realm.ApiId,
          game.GggApiTradeIdentifier,
          defaultLeagueLookup[realm.GameId]);
      })
      .ToList();

    return TypedResults.Ok(response);
  }

  private static string GetGameDisplay(string gameApiId) => gameApiId switch
  {
    "poe" => "poe1",
    "poe2" => "poe2",
    _ => gameApiId
  };

  private static int GetGameSortOrder(string gameApiId) => gameApiId switch
  {
    "poe" => 0,
    "poe2" => 1,
    _ => 99
  };

  private static int GetRealmSortOrder(string realmApiId) => realmApiId switch
  {
    "pc" => 0,
    "poe2" => 0,
    "xbox" => 1,
    "sony" => 2,
    _ => 99
  };

  public record GetResponse(
    string Value,
    string Label,
    string GameApiId,
    string RealmApiId,
    string TradeApiPath,
    string DefaultLeagueValue);
}
