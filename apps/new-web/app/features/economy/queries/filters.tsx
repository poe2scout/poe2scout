import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";

type Filter = {
  displayName: string;
  category: string;
  identifier: string;
};

type GetFiltersResponse = {
  filters: Filter[];
};

export default function getFiltersQueryOptions(realmApiId: string) {
  return queryOptions({
    queryKey: ["filters", realmApiId],
    queryFn: () =>
      fetchRoute(
        `/api/${realmApiId}/Static/Filters`,
      ) as Promise<GetFiltersResponse>,
  });
}
