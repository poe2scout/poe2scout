import { useSuspenseQuery } from "@tanstack/react-query";
import { useLocation, useSearchParams } from "react-router";
import { queryClient } from "~/shared/api/query-client";
import { useLeagueContext } from "~/features/league/context";
import getNumberNonZero from "~/shared/utils/get-number-non-zero";
import type { BreadcrumbHandle } from "~/features/app-shell/components/header-breadcrumbs";
import type { Route } from "./+types/currencies";
import getCurrencyItemsQueryOptions from "../queries/currency-items";
import { getEconomyTableColumns } from "../components/economy-table-columns";
import EconomyTable from "../components/economy-table";
import { CURRENCY_PRICE_HISTORY_CONFIG } from "../history-config";
import {
  createPageMeta,
  formatTitle,
  getCategoryLabel,
  getLeagueContextTitle,
} from "~/shared/meta/page-title";
import { getEconomyItemRouteSegment } from "../utils";
import { getLeagueBaseCurrencyIdentifier } from "~/features/league/currency-identifier";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: params.category,
  }),
};

export function meta({ matches, params }: Route.MetaArgs) {
  const categoryLabel = getCategoryLabel(
    matches,
    "currencies",
    params.category,
  );
  const leagueContext = getLeagueContextTitle(matches);
  const title = formatTitle([`${categoryLabel} Prices`, leagueContext]);
  const context = leagueContext ?? "the selected league";

  return createPageMeta({
    title,
    description: `Check current ${categoryLabel} currency prices, trade values, and Path of Exile 2 market data for ${context}.`,
  });
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
    getCurrencyItemsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      category: params.category,
      referenceCurrency,
      search,
      page,
      perPage,
      historyConfig: CURRENCY_PRICE_HISTORY_CONFIG,
    }),
  );

  return {
    referenceCurrency,
    search,
    page,
    perPage,
    historyConfig: CURRENCY_PRICE_HISTORY_CONFIG,
  };
}

export default function CurrencyCategory({
  params,
  loaderData,
}: Route.ComponentProps) {
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const { league, realm } = useLeagueContext();
  const { data } = useSuspenseQuery(
    getCurrencyItemsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      category: params.category,
      referenceCurrency: loaderData.referenceCurrency,
      search: loaderData.search,
      page: loaderData.page,
      perPage: loaderData.perPage,
      historyConfig: loaderData.historyConfig,
    }),
  );

  const referenceCurrency =
    loaderData.referenceCurrency ?? getLeagueBaseCurrencyIdentifier(league);

  const columns = getEconomyTableColumns({
    realm,
    league,
    referenceCurrency,
    priceHistoryConfig: loaderData.historyConfig,
    getItemTo: (item) => `${getEconomyItemRouteSegment(item)}${location.search}`,
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
