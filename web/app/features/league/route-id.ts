import type { League } from "./types";

export function getLeagueRouteId(league: Pick<League, "shortName">) {
  return league.shortName;
}

export function findLeagueByRouteId(
  leagues: League[],
  routeId: string | undefined,
) {
  return leagues.find((league) => league.shortName === routeId);
}
