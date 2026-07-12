import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";
import {
  type ExchangeSnapshotPairPayload,
  normalizeSnapshotPair,
} from "./query-utils";

export function getSnapshotPairsQueryOptions({
  realmApiId,
  leagueName,
  baseCurrencyApiIds,
}: {
  realmApiId: string;
  leagueName: string;
  baseCurrencyApiIds: string[];
}) {
  return queryOptions({
    queryKey: [
      "exchange",
      "snapshot-pairs",
      { realmApiId, leagueName, baseCurrencyApiIds },
    ],
    queryFn: async () => {
      const payload = (await fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/SnapshotPairs`,
      )) as ExchangeSnapshotPairPayload[];
      const baseCurrencyApiIdSet = new Set(baseCurrencyApiIds);

      return payload.map((row) =>
        normalizeSnapshotPair(row, baseCurrencyApiIdSet),
      );
    },
  });
}
