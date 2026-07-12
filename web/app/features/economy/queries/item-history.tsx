import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";
import toQueryString from "~/shared/utils/to-query-string";
import type {
  ItemDailyStatsHistoryResponse,
  ItemHistoryResponse,
} from "../types";

export function getItemHistoryQueryOptions({
  realmApiId,
  leagueName,
  itemId,
  logCount,
  referenceCurrency,
  endTime,
}: {
  realmApiId: string;
  leagueName: string;
  itemId: number;
  logCount: number;
  referenceCurrency: string;
  endTime: string;
}) {
  return queryOptions({
    queryKey: [
      "item-history",
      "raw",
      { realmApiId, leagueName, itemId, logCount, referenceCurrency, endTime },
    ],
    queryFn: () => {
      const query = toQueryString({
        LogCount: logCount,
        ReferenceCurrency: referenceCurrency,
        EndTime: endTime,
      });

      return fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/Items/${itemId}/History${query}`,
      ) as Promise<ItemHistoryResponse>;
    },
  });
}

export function getItemDailyStatsHistoryQueryOptions({
  realmApiId,
  leagueName,
  itemId,
  dayCount,
  endDate,
}: {
  realmApiId: string;
  leagueName: string;
  itemId: number;
  dayCount: number;
  endDate?: string;
}) {
  return queryOptions({
    queryKey: [
      "item-history",
      "daily",
      { realmApiId, leagueName, itemId, dayCount, endDate },
    ],
    queryFn: () => {
      const query = toQueryString({
        DayCount: dayCount,
        EndDate: endDate,
      });

      return fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/Items/${itemId}/DailyStatsHistory${query}`,
      ) as Promise<ItemDailyStatsHistoryResponse>;
    },
  });
}
