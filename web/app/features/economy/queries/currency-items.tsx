import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";
import toQueryString from "~/shared/utils/to-query-string";
import type {
  CurrencyEconomyItem,
  PaginatedEconomyResponse as PaginatedResponse,
} from "../types";
import type { CategoryPriceHistoryConfig } from "../history-config";

export type GetCurrencyItemsResponse = PaginatedResponse<CurrencyEconomyItem>;

export default function getCurrencyItemsQueryOptions({
  realmApiId,
  leagueName,
  category,
  referenceCurrency,
  search,
  page,
  perPage,
  historyConfig,
}: {
  realmApiId: string;
  leagueName: string;
  category: string;
  referenceCurrency: string | null;
  search: string | null;
  page: Number | null;
  perPage: Number | null;
  historyConfig: CategoryPriceHistoryConfig;
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
        dataPoints: historyConfig.dataPoints,
        frequencyHours: historyConfig.frequencyHours,
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
        DataPoints: historyConfig.dataPoints,
        FrequencyHours: historyConfig.frequencyHours,
      });

      return fetchRoute(
        `${baseUrl}${query}`,
      ) as Promise<GetCurrencyItemsResponse>;
    },
  });
}
