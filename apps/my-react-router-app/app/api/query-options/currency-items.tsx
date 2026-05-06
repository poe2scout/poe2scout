import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "../fetch-route";
import toQueryString from "~/utils/to-query-string";

type PriceLog = {
  price: number;
  time: string;
  quantity: number;
}[];

type CurrencyItem = {
  currencyItemId: number;
  itemId: number;
  currencyCategoryId: number;
  apiId: string;
  text: string;
  categoryApiId: string;
  iconUrl: string;
  itemMetaData: any;
  priceLogs: PriceLog | null;
  currentPrice: number;
  currentQuantity: number;
};

type GetCurrencyItemsResponse = {
  currentPage: number;
  pages: number;
  total: number;
  items: CurrencyItem[];
};

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
  page: string | null;
  perPage: string | null;
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
