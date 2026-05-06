import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "../fetch-route";
import toQueryString from "~/utils/to-query-string";

type PriceLog = {
  price: number;
  time: string;
  quantity: number;
}[];

type UniqueItem = {
  uniqueItemId: number;
  itemId: number;
  iconUrl: string;
  text: string;
  name: string;
  categoryApiId: string;
  itemMetaData: any;
  type: string;
  priceLogs: PriceLog | null;
  currentPrice: number;
  currentQuantity: number;
};

type GetUniqueItemsResponse = {
  currentPage: number;
  pages: number;
  total: number;
  items: UniqueItem[];
};

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
