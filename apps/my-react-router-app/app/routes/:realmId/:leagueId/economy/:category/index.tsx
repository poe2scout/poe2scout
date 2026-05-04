import type { Route } from "./+types";
import getCurrencyItemsQueryOptions from "~/api/query-options/currency-items";
import { queryClient } from "~/api/query-client";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useLoaderData } from "react-router";

export async function clientLoader({
  request,
  params,
}: Route.ClientLoaderArgs) {
  const url = new URL(request.url);
  const queryParams = url.searchParams;
  const referenceCurrency = queryParams.get("referenceCurrency");
  const search = queryParams.get("search");
  const page = queryParams.get("page");
  const perPage = queryParams.get("perPage");

  await queryClient.prefetchQuery(
    getCurrencyItemsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      category: params.category,
      referenceCurrency: referenceCurrency,
      search: search,
      page: page,
      perPage: perPage,
    }),
  );

  return {
    referenceCurrency,
    search,
    page,
    perPage,
  };
}

export default function Economy({ params }: Route.ComponentProps) {
  const loaderData = useLoaderData<typeof clientLoader>();

  const { data, isPending } = useSuspenseQuery(
    getCurrencyItemsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      category: params.category,
      referenceCurrency: loaderData.referenceCurrency,
      search: loaderData.search,
      page: loaderData.page,
      perPage: loaderData.perPage,
    }),
  );

  return <></>;
}
