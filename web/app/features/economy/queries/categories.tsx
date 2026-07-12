import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "~/shared/api/fetch-route";

type CurrencyCategory = {
  apiId: string;
  currencyCategoryId: number;
  icon: string;
  label: string;
};

type UniqueCategory = {
  apiId: string;
  itemCategoryId: number;
  icon: string;
  label: string;
};

type GetCategoriesResponse = {
  currencyCategories: CurrencyCategory[];
  uniqueCategories: UniqueCategory[];
};

export default function getCategoriesQueryOptions(
  realmApiId: string,
  leagueName: string,
) {
  return queryOptions({
    queryKey: ["categories", { realmApiId, leagueName }],
    queryFn: async () =>
      (await fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/Items/Categories`,
      )) as Promise<GetCategoriesResponse>,
  });
}
