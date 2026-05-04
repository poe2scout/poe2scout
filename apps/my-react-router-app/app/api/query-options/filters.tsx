import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "../fetch-route";

export default function getFiltersQueryOptions(realmApiId: string) {
  return queryOptions({
    queryKey: ["filters", realmApiId],
    queryFn: () =>
      fetchRoute(`/api/${realmApiId}/Static/Filters`) as Promise<{
        filters: {
          displayName: string;
          category: string;
          identifier: string;
        }[];
      }>,
  });
}
