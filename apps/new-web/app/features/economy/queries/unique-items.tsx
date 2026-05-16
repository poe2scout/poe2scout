import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "../../../shared/api/fetch-route";
import toQueryString from "~/shared/utils/to-query-string";
import type { PaginatedEconomyResponse, UniqueEconomyItem } from "../types";

export type GetUniqueItemsResponse =
  PaginatedEconomyResponse<UniqueEconomyItem>;

export default function getUniqueItemsQueryOptions({
  realmApiId,
  leagueName,
  category,
  referenceCurrency,
  search,
  page,
  perPage,
}: {
  realmApiId: string;
  leagueName: string;
  category: string;
  referenceCurrency: string | null;
  search: string | null;
  page: number | null;
  perPage: number | null;
}) {
  return queryOptions({
    queryKey: [
      "unique-items",
      "list",
      {
        realmApiId,
        leagueName,
        category,
        referenceCurrency,
        search,
        page,
        perPage,
      },
    ],
    queryFn: () => {
      const baseUrl = `/api/${realmApiId}/Leagues/${leagueName}/Uniques/ByCategory`;
      const query = toQueryString({
        Category: category,
        ReferenceCurrency: referenceCurrency,
        Search: search,
        Page: page,
        PerPage: perPage,
      });

      return fetchRoute(
        `${baseUrl}${query}`,
      ) as Promise<GetUniqueItemsResponse>;
    },
  });
}
