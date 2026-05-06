import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "../fetch-route";
import toQueryString from "~/utils/to-query-string";
import type {
  CurrencyEconomyItem,
  PaginatedEconomyResponse,
} from "~/types/economy";

export type GetCurrencyItemsResponse =
  PaginatedEconomyResponse<CurrencyEconomyItem>;

export default function getCurrencyItemsQueryOptions({
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
  page: Number | null;
  perPage: Number | null;
}) {
  return queryOptions({
    queryKey: [
      "currency-items",
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
      const baseUrl = `/api/${realmApiId}/Leagues/${leagueName}/Currencies/ByCategory`;
      const query = toQueryString({
        Category: category,
        ReferenceCurrency: referenceCurrency,
        Search: search,
        Page: page,
        PerPage: perPage,
      });

      return fetchRoute(
        `${baseUrl}${query}`,
      ) as Promise<GetCurrencyItemsResponse>;
    },
  });
}
