import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "../fetch-route";
import toQueryString from "~/utils/to-query-string";

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
  page: string | null;
  perPage: string | null;
}) {
  return queryOptions({
    queryKey: [
      "uniques",
      "items",
      realmApiId,
      leagueName,
      category,
      referenceCurrency,
      search,
      page,
      perPage,
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

      return fetchRoute(`${baseUrl}${query}`) as Promise<{
        currentPage: number;
        pages: number;
        total: number;
        items: {
          uniqueItemId: number;
          itemId: number;
          iconUrl: string;
          text: string;
          name: string;
          categoryApiId: string;
          itemMetaData: any;
          type: string;
          priceLogs: { price: number; time: string; quantity: number }[] | null;
          currentPrice: number;
          currentQuantity: number;
        }[];
      }>;
    },
  });
}
