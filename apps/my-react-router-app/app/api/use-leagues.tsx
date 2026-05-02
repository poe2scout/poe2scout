import { queryOptions } from "@tanstack/react-query";
import type League from "~/types/league";
import fetchRoute from "./fetch-route";

export default function getLeaguesQueryOptions(realmApiId: string) {
  return queryOptions({
    queryKey: ["leagues", realmApiId],
    queryFn: async () =>
      (await fetchRoute(`/api/${realmApiId}/Leagues`)) as Promise<League[]>,
  });
}
