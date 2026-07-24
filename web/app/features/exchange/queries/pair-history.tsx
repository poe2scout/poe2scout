import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";
import toQueryString from "~/shared/utils/to-query-string";
import type { ExchangePairHistoryResponse } from "../types";
import {
  type ExchangePairHistoryEntryPayload,
  normalizePairHistoryEntry,
} from "./query-utils";

type PairHistoryPayload = {
  history?: ExchangePairHistoryEntryPayload[];
  meta?: {
    hasMore?: boolean;
  };
  baseCurrencyApiId?: string | null;
  baseCurrencyBaseItemTypeId?: string | null;
  baseCurrencyText?: string;
};

export function getPairHistoryQueryOptions({
  realmApiId,
  leagueName,
  currencyOneItemId,
  currencyTwoItemId,
  limit,
  endEpoch,
}: {
  realmApiId: string;
  leagueName: string;
  currencyOneItemId: number;
  currencyTwoItemId: number;
  limit: number;
  endEpoch?: number;
}) {
  return queryOptions({
    queryKey: [
      "exchange",
      "pair-history",
      {
        realmApiId,
        leagueName,
        currencyOneItemId,
        currencyTwoItemId,
        limit,
        endEpoch,
      },
    ],
    queryFn: async (): Promise<ExchangePairHistoryResponse> => {
      const query = toQueryString({
        Limit: limit,
        EndEpoch: endEpoch,
      });
      const payload = (await fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/Currencies/Pairs/${currencyOneItemId}/${currencyTwoItemId}/History${query}`,
      )) as PairHistoryPayload;

      return {
        history: (payload.history ?? []).map(normalizePairHistoryEntry),
        hasMore: Boolean(payload.meta?.hasMore),
        baseCurrencyApiId: payload.baseCurrencyApiId ?? null,
        baseCurrencyBaseItemTypeId:
          payload.baseCurrencyBaseItemTypeId ?? null,
        baseCurrencyText: payload.baseCurrencyText ?? "",
      };
    },
  });
}
