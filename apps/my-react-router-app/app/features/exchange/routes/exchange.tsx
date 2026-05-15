import type { BreadcrumbHandle } from "~/features/app-shell/components/header-breadcrumbs";
import { useLeagueContext } from "~/features/league/context";
import { queryClient } from "~/shared/api/query-client";
import type { Route } from "./+types/exchange";
import ExchangePairTable from "~/features/exchange/components/exchange-pair-table";
import ExchangeSummary from "~/features/exchange/components/exchange-summary";
import MarketHistoryChart from "~/features/exchange/components/market-history-chart";
import { getExchangeSnapshotQueryOptions } from "~/features/exchange/queries/exchange-snapshot";
import { getSnapshotHistoryQueryOptions } from "~/features/exchange/queries/snapshot-history";
import { getSnapshotPairsQueryOptions } from "~/features/exchange/queries/snapshot-pairs";
import type {
  ExchangeOrder,
  ExchangeSort,
  ExchangeTableState,
} from "~/features/exchange/types";
import { useSuspenseQuery } from "@tanstack/react-query";
import getNumberNonZero from "~/shared/utils/get-number-non-zero";

export const handle: BreadcrumbHandle = {
  breadcrumb: () => ({ label: "Currency Exchange" }),
};

const HISTORY_LIMIT = 24 * 14;
const DEFAULT_TABLE_STATE: ExchangeTableState = {
  search: "",
  sort: "volume",
  order: "desc",
  page: 1,
  perPage: 25,
};

export async function clientLoader({
  request,
  params,
}: Route.ClientLoaderArgs) {
  const url = new URL(request.url);
  const tableState = getExchangeTableState(url.searchParams);

  await Promise.all([
    queryClient.prefetchQuery(
      getExchangeSnapshotQueryOptions({
        realmApiId: params.realmId,
        leagueName: params.leagueId,
      }),
    ),
    queryClient.prefetchQuery(
      getSnapshotHistoryQueryOptions({
        realmApiId: params.realmId,
        leagueName: params.leagueId,
        limit: HISTORY_LIMIT,
      }),
    ),
    queryClient.prefetchQuery(
      getSnapshotPairsQueryOptions({
        realmApiId: params.realmId,
        leagueName: params.leagueId,
      }),
    ),
  ]);

  return tableState;
}

export default function Exchange({ params, loaderData }: Route.ComponentProps) {
  const { league } = useLeagueContext();
  const { data: snapshot } = useSuspenseQuery(
    getExchangeSnapshotQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
    }),
  );
  const { data: history } = useSuspenseQuery(
    getSnapshotHistoryQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      limit: HISTORY_LIMIT,
    }),
  );
  const { data: pairs } = useSuspenseQuery(
    getSnapshotPairsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
    }),
  );

  return (
    <div className="flex flex-col gap-4 py-4">
      <ExchangeSummary league={league} snapshot={snapshot} />
      <MarketHistoryChart
        history={history.data}
        baseCurrencyText={history.baseCurrencyText || snapshot.baseCurrencyText}
      />
      <ExchangePairTable pairs={pairs} tableState={loaderData} />
    </div>
  );
}

function getExchangeTableState(
  searchParams: URLSearchParams,
): ExchangeTableState {
  return {
    search: searchParams.get("search") ?? DEFAULT_TABLE_STATE.search,
    sort: getSort(searchParams.get("sort")),
    order: getOrder(searchParams.get("order")),
    page:
      getNumberNonZero(searchParams.get("page")) ?? DEFAULT_TABLE_STATE.page,
    perPage:
      getNumberNonZero(searchParams.get("perPage")) ??
      DEFAULT_TABLE_STATE.perPage,
  };
}

function getSort(value: string | null): ExchangeSort {
  return value === "pair" || value === "volume"
    ? value
    : DEFAULT_TABLE_STATE.sort;
}

function getOrder(value: string | null): ExchangeOrder {
  return value === "asc" || value === "desc"
    ? value
    : DEFAULT_TABLE_STATE.order;
}
