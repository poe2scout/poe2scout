import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";

export type Filter = {
  displayName: string;
  category: string;
  identifier: string;
  itemKind: "currency" | "unique";
};

type GetFiltersResponse = {
  filters: Filter[];
};

export default function getFiltersQueryOptions(realmApiId: string) {
  return queryOptions({
    queryKey: ["filters", realmApiId],
    queryFn: () =>
      fetchRoute(
        `/api/Realms/${realmApiId}/Filters`,
      ) as Promise<GetFiltersResponse>,
  });
}
