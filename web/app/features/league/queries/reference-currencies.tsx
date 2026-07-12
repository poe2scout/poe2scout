import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";
import type { LeagueCurrency } from "../types";

export default function getReferenceCurrenciesQueryOptions(
  realmApiId: string,
  leagueName: string,
) {
  return queryOptions({
    queryKey: ["reference-currencies", realmApiId, leagueName],
    queryFn: async () =>
      (await fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/ReferenceCurrencies`,
      )) as Promise<LeagueCurrency[]>,
  });
}
