import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";
import { type ExchangeSnapshotPayload, normalizeSnapshot } from "./query-utils";

export function getExchangeSnapshotQueryOptions({
  realmApiId,
  leagueName,
}: {
  realmApiId: string;
  leagueName: string;
}) {
  return queryOptions({
    queryKey: ["exchange", "snapshot", { realmApiId, leagueName }],
    queryFn: async () => {
      const payload = await fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/ExchangeSnapshot`,
      );

      return normalizeSnapshot(payload as ExchangeSnapshotPayload);
    },
  });
}
