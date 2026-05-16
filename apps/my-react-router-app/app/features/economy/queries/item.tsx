import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";
import type { ItemSummary } from "../types";

export default function getItemQueryOptions({
  realmApiId,
  leagueName,
  itemId,
}: {
  realmApiId: string;
  leagueName: string;
  itemId: number;
}) {
  return queryOptions({
    queryKey: ["items", "detail", { realmApiId, leagueName, itemId }],
    queryFn: () =>
      fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/Items/${itemId}`,
      ) as Promise<ItemSummary>,
  });
}
