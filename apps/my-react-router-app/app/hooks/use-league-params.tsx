import { useParams } from "react-router";

export default function useLeagueParams(): {
  isLeagueSelected: boolean;
  realmId: string | null;
  leagueId: string | null;
} {
  const values = useParams();
  const realmId = values.realmId ?? null;
  const leagueId = values.leagueId ?? null;
  return {
    isLeagueSelected: realmId !== null && leagueId !== null,
    realmId: realmId,
    leagueId: leagueId,
  };
}
