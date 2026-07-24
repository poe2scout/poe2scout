import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";
import toQueryString from "~/shared/utils/to-query-string";
import type { SnapshotHistoryResponse } from "../types";
import { type ExchangeSnapshotPayload, normalizeSnapshot } from "./query-utils";

type SnapshotHistoryPayload = {
  data?: ExchangeSnapshotPayload[];
  meta?: {
    hasMore?: boolean;
  };
  baseCurrencyApiId?: string | null;
  baseCurrencyBaseItemTypeId?: string | null;
  baseCurrencyText?: string;
};

export function getSnapshotHistoryQueryOptions({
  realmApiId,
  leagueName,
  limit,
  endEpoch,
}: {
  realmApiId: string;
  leagueName: string;
  limit: number;
  endEpoch?: number;
}) {
  return queryOptions({
    queryKey: [
      "exchange",
      "snapshot-history",
      { realmApiId, leagueName, limit, endEpoch },
    ],
    queryFn: async (): Promise<SnapshotHistoryResponse> => {
      const query = toQueryString({ Limit: limit, EndEpoch: endEpoch });
      const payload = (await fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/SnapshotHistory${query}`,
      )) as SnapshotHistoryPayload;

      return {
        data: (payload.data ?? []).map(normalizeSnapshot),
        hasMore: Boolean(payload.meta?.hasMore),
        baseCurrencyApiId: payload.baseCurrencyApiId ?? null,
        baseCurrencyBaseItemTypeId:
          payload.baseCurrencyBaseItemTypeId ?? null,
        baseCurrencyText: payload.baseCurrencyText ?? "",
      };
    },
  });
}
