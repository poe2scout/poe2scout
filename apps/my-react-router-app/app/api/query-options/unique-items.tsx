import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "../fetch-route";

export default function getUniqueItemsQueryOptions(
  realmApiId: string,
  leagueName: string,
  category: string,
  referenceCurrency: string,
  search: string,
  page: number,
  perPage: number,
) {
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
    queryFn: () =>
      fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/Uniques/ByCategory?Category=${category}&ReferenceCurrency=${referenceCurrency}&Search=${search}&Page=${page}&PerPage=${perPage}`,
      ) as Promise<{
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
      }>,
  });
}
