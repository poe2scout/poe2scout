import { createContext, useContext } from "react";
import type League from "~/types/league";
import type Realm from "~/types/realm";

type LeagueContextValue = {
  league: League;
  realm: Realm;
};

export const LeagueContext = createContext<LeagueContextValue | null>(null);

export function useLeagueContext() {
  const context = useContext(LeagueContext);

  if (!context) {
    throw new Error("useLeagueContext must be used inside LeagueContext");
  }

  return context;
}
