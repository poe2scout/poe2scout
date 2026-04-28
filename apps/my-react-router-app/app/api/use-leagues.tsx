import { useQuery } from "@tanstack/react-query";
import * as changeKeys from "change-case/keys";
import type League from "~/types/league";

async function FetchLeagues(realmApiId: string): Promise<League[]> {
  const response = await fetch(`api/${realmApiId}/Leagues`);
  return changeKeys.camelCase(await response.json(), 10) as League[];
}

export default function useLeagues(realmApiId: string) {
  return useQuery({
    queryKey: [`leagues|${realmApiId}`],
    queryFn: () => FetchLeagues(realmApiId),
  });
}
