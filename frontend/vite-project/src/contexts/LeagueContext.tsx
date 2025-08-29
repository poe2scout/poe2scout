import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

export interface League {
  value: string;
  divinePrice: number;
}

interface LeagueContextType {
  league: League;
  setLeague: (league: League) => void;
  leagues: League[];
  loading: boolean;
}

const LeagueContext = createContext<LeagueContextType | undefined>(undefined);

const DEFAULT_LEAGUE = "Rise of the Abbysal"

export function LeagueProvider({ children }: { children: ReactNode }) {
  const [leagues, setLeagues] = useState<League[]>([]);
  const [loading, setLoading] = useState(true);
  const [league, setLeague] = useState<League>({ value: DEFAULT_LEAGUE, divinePrice: 100 });

  const fetchLeagues = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/leagues`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setLeagues(data);
      
      const updatedLeague = data.find((l: League) => l.value === league.value);

      setLeague(updatedLeague);
    } catch (error) {
      console.error("Error fetching leagues:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeagues(); 

    const intervalId = setInterval(fetchLeagues, 3600000);

    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    localStorage.setItem("league2", JSON.stringify(league));
  }, [league]);

  return (
    <LeagueContext.Provider value={{ league, setLeague, leagues, loading }}>
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
