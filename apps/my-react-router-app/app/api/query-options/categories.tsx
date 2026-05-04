import { queryOptions } from "@tanstack/react-query";
import fetchRoute from "../fetch-route";

export default function getCategoriesQueryOptions(
  realmApiId: string,
  leagueName: string,
) {
  return queryOptions({
    queryKey: ["categories", realmApiId, leagueName],
    queryFn: async () =>
      (await fetchRoute(
        `/api/${realmApiId}/Items/Categories?LeagueName=${leagueName}`,
      )) as Promise<{
        currencyCategories: {
          apiId: string;
          currencyCategoryId: number;
          icon: string;
          label: string;
        }[];
        uniqueCategories: {
          apiId: string;
          itemCategoryId: number;
          icon: string;
          label: string;
        }[];
      }>,
  });
}
