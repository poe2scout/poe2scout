import { useSuspenseQuery } from "@tanstack/react-query";
import { useLoaderData } from "react-router";
import { queryClient } from "~/api/query-client";
import getUniqueItemsQueryOptions from "~/api/query-options/unique-items";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";
import type { Route } from "./+types";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: params.category,
  }),
};

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

  queryClient.prefetchQuery(
    getUniqueItemsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      category: params.category,
      referenceCurrency,
      search,
      page,
      perPage,
    }),
  );

  return {
    referenceCurrency,
    search,
    page,
    perPage,
  };
}

export default function UniqueCategory({ params }: Route.ComponentProps) {
  const loaderData = useLoaderData<typeof clientLoader>();

  const { data } = useSuspenseQuery(
    getUniqueItemsQueryOptions({
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
