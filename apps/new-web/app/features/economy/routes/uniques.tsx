import { useSuspenseQuery } from "@tanstack/react-query";
import { useLocation, useSearchParams } from "react-router";
import { queryClient } from "~/shared/api/query-client";
import { useLeagueContext } from "~/features/league/context";
import getNumberNonZero from "~/shared/utils/get-number-non-zero";
import type { BreadcrumbHandle } from "~/features/app-shell/components/header-breadcrumbs";
import type { Route } from "./+types/uniques";
import getUniqueItemsQueryOptions from "../queries/unique-items";
import { getEconomyTableColumns } from "../components/economy-table-columns";
import EconomyTable from "../components/economy-table";
import {
  formatTitle,
  getCategoryLabel,
  getLeagueContextTitle,
} from "~/shared/meta/page-title";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: params.category,
  }),
};

export function meta({ matches, params }: Route.MetaArgs) {
  const categoryLabel = getCategoryLabel(matches, "uniques", params.category);
  const leagueContext = getLeagueContextTitle(matches);

  return [
    { title: formatTitle([`${categoryLabel} Unique Prices`, leagueContext]) },
  ];
}

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
  const location = useLocation();
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
      getRowTo={(item) => `${item.itemId}${location.search}`}
    />
  );
}
