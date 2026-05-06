import { useSuspenseQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router";
import { queryClient } from "~/api/query-client";
import getUniqueItemsQueryOptions from "~/api/query-options/unique-items";
import EconomyTable from "~/components/economy/economy-table";
import { getEconomyTableColumns } from "~/components/economy/economy-table-columns";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";
import { useLeagueContext } from "~/contexts/league-context";
import type { Route } from "./+types";
import getNumberNonZero from "~/utils/get-number-non-zero";

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
  const page = getNumberNonZero(queryParams.get("page")) ?? 1;
  const perPage = getNumberNonZero(queryParams.get("perPage")) ?? 25;

  await queryClient.prefetchQuery(
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

export default function UniqueCategory({
  params,
  loaderData,
}: Route.ComponentProps) {
  const [searchParams, setSearchParams] = useSearchParams();
  const { league, realm } = useLeagueContext();
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
  const referenceCurrency =
    loaderData.referenceCurrency ?? league.baseCurrencyApiId;
  const columns = getEconomyTableColumns({
    realm,
    league,
    referenceCurrency,
  });

  const updatePagination = (page: number, perPage: number) => {
    const nextSearchParams = new URLSearchParams(searchParams);
    nextSearchParams.set("page", String(page));
    nextSearchParams.set("perPage", String(perPage));

    setSearchParams(nextSearchParams);
  };

  return (
    <EconomyTable
      items={data.items}
      page={data.currentPage}
      pages={data.pages}
      totalItems={data.total}
      columns={columns}
      rowsPerPage={loaderData.perPage}
      onPaginationChange={updatePagination}
      rowsPerPageOptions={[10, 25, 50, 100]}
    />
  );
}
