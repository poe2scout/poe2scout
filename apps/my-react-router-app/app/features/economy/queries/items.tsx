import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";
import type { ItemSummary } from "../types";

export default function getItemsQueryOptions({
  realmApiId,
  leagueName,
}: {
  realmApiId: string;
  leagueName: string;
}) {
  return queryOptions({
    queryKey: ["items", "list", { realmApiId, leagueName }],
    queryFn: () =>
      fetchRoute(`/api/${realmApiId}/Leagues/${leagueName}/Items`) as Promise<
        ItemSummary[]
      >,
  });
}
