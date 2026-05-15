import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";
import {
  type ExchangeSnapshotPairPayload,
  normalizeSnapshotPair,
} from "./query-utils";

export function getSnapshotPairsQueryOptions({
  realmApiId,
  leagueName,
}: {
  realmApiId: string;
  leagueName: string;
}) {
  return queryOptions({
    queryKey: ["exchange", "snapshot-pairs", { realmApiId, leagueName }],
    queryFn: async () => {
      const payload = (await fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/SnapshotPairs`,
      )) as ExchangeSnapshotPairPayload[];

      return payload.map(normalizeSnapshotPair);
    },
  });
}
