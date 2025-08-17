namespace Poe2scout.Database.Models;

public class League(int leagueId, string name)
{
    public int LeagueId { get; } = leagueId;
    public string Name { get; } = name;
}