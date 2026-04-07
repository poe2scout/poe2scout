import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import {
  fetchLeagues as fetchLeaguesFromApi,
  fetchRealmOptions as fetchRealmOptionsFromApi,
} from "../api/economy";
import { setActiveRealmPath } from "../api/client";
import type { RealmOption } from "../types";

export interface League {
  value: string;
  divinePrice: number;
  chaosDivinePrice: number;
  baseCurrencyApiId: string;
  baseCurrencyText: string;
  baseCurrencyIconUrl: string | null;
  exaltedCurrencyText: string;
  exaltedCurrencyIconUrl: string | null;
  divineCurrencyText: string;
  divineCurrencyIconUrl: string | null;
  chaosCurrencyText: string;
  chaosCurrencyIconUrl: string | null;
}

interface LeagueContextType {
  realm: RealmOption;
  setRealm: (realm: RealmOption) => void;
  realms: RealmOption[];
  league: League;
  setLeague: (league: League) => void;
  leagues: League[];
  loading: boolean;
}

const LeagueContext = createContext<LeagueContextType | undefined>(undefined);

const DEFAULT_REALM = "poe2/poe2";
const REALM_STORAGE_KEY = "poe2scout.realmSelection";
const LEAGUE_STORAGE_KEY = "poe2scout.leagueSelections";
const EMPTY_LEAGUE: League = {
  value: "",
  divinePrice: 100,
  chaosDivinePrice: 50,
  baseCurrencyApiId: "exalted",
  baseCurrencyText: "Exalted Orb",
  baseCurrencyIconUrl: null,
  exaltedCurrencyText: "Exalted Orb",
  exaltedCurrencyIconUrl: null,
  divineCurrencyText: "Divine Orb",
  divineCurrencyIconUrl: null,
  chaosCurrencyText: "Chaos Orb",
  chaosCurrencyIconUrl: null,
};

const getStoredLeagueSelections = (): Record<string, string> => {
  const stored = localStorage.getItem(LEAGUE_STORAGE_KEY);

  if (!stored) {
    return {};
  }

  try {
    return JSON.parse(stored) as Record<string, string>;
  } catch {
    return {};
  }
};

const persistLeagueSelection = (realmValue: string, leagueValue: string): void => {
  const nextSelections = {
    ...getStoredLeagueSelections(),
    [realmValue]: leagueValue,
  };
  localStorage.setItem(LEAGUE_STORAGE_KEY, JSON.stringify(nextSelections));
};

export function LeagueProvider({ children }: { children: ReactNode }) {
  const [realms, setRealms] = useState<RealmOption[]>([]);
  const [realm, setRealmState] = useState<RealmOption | null>(null);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [loading, setLoading] = useState(true);
  const [league, setLeagueState] = useState<League>(EMPTY_LEAGUE);

  const setLeague = (nextLeague: League) => {
    setLeagueState(nextLeague);

    if (realm) {
      persistLeagueSelection(realm.value, nextLeague.value);
    }
  };

  const setRealm = (nextRealm: RealmOption) => {
    setLoading(true);
    setLeagues([]);
    setLeagueState(EMPTY_LEAGUE);
    setActiveRealmPath(nextRealm.realmApiId);
    setRealmState(nextRealm);
  };

  useEffect(() => {
    let isMounted = true;

    const fetchRealms = async () => {
      try {
        setLoading(true);
        const options = await fetchRealmOptionsFromApi();

        if (!isMounted) {
          return;
        }

        setRealms(options);

        const storedRealmValue = localStorage.getItem(REALM_STORAGE_KEY);
        const nextRealm =
          options.find((option) => option.value === storedRealmValue) ??
          options.find((option) => option.value === DEFAULT_REALM) ??
          options[0] ??
          null;

        if (nextRealm) {
          setRealm(nextRealm);
        }
      } catch (error) {
        console.error("Error fetching realms:", error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchRealms();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!realm) {
      return;
    }

    let isMounted = true;
    setActiveRealmPath(realm.realmApiId);
    localStorage.setItem(REALM_STORAGE_KEY, realm.value);

    const fetchLeagues = async () => {
      try {
        setLoading(true);
        const data = await fetchLeaguesFromApi();
        const nextLeagues = data.map(
          (leagueRecord): League => ({
            value: leagueRecord.value,
            divinePrice: leagueRecord.divinePrice,
            chaosDivinePrice: leagueRecord.chaosDivinePrice,
            baseCurrencyApiId: leagueRecord.baseCurrencyApiId,
            baseCurrencyText: leagueRecord.baseCurrencyText,
            baseCurrencyIconUrl: leagueRecord.baseCurrencyIconUrl,
            exaltedCurrencyText: leagueRecord.exaltedCurrencyText,
            exaltedCurrencyIconUrl: leagueRecord.exaltedCurrencyIconUrl,
            divineCurrencyText: leagueRecord.divineCurrencyText,
            divineCurrencyIconUrl: leagueRecord.divineCurrencyIconUrl,
            chaosCurrencyText: leagueRecord.chaosCurrencyText,
            chaosCurrencyIconUrl: leagueRecord.chaosCurrencyIconUrl,
          }),
        );

        if (!isMounted) {
          return;
        }

        setLeagues(nextLeagues);

        const storedLeagueSelections = getStoredLeagueSelections();
        const nextLeague =
          nextLeagues.find(
            (option) => option.value === storedLeagueSelections[realm.value],
          ) ??
          nextLeagues.find(
            (option) => option.value === realm.defaultLeagueValue,
          ) ??
          nextLeagues[0] ??
          EMPTY_LEAGUE;

        setLeagueState(nextLeague);

        if (nextLeague.value) {
          persistLeagueSelection(realm.value, nextLeague.value);
        }
      } catch (error) {
        console.error("Error fetching leagues:", error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchLeagues();

    const intervalId = setInterval(fetchLeagues, 3600000);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [realm]);

  useEffect(() => {
    if (!realm || !league.value) {
      return;
    }

    persistLeagueSelection(realm.value, league.value);
  }, [league, realm]);

  if (!realm) {
    return null;
  }

  return (
    <LeagueContext.Provider
      value={{
        realm,
        setRealm,
        realms,
        league,
        setLeague,
        leagues,
        loading,
      }}
    >
      {children}
    </LeagueContext.Provider>
  );
}

export function useLeague() {
  const context = useContext(LeagueContext);
  if (context === undefined) {
    throw new Error("useLeague must be used within a LeagueProvider");
  }
  return context;
}
