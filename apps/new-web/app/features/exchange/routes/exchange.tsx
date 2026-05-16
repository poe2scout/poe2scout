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
import { useQuery, useSuspenseQuery } from "@tanstack/react-query";
import getNumberNonZero from "~/shared/utils/get-number-non-zero";
import getLeaguesQueryOptions from "~/features/league/queries/leagues";
import getReferenceCurrenciesQueryOptions from "~/features/league/queries/reference-currencies";
import type { LeagueCurrency } from "~/features/league/types";

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
  const snapshotPrefetch = queryClient.prefetchQuery(
    getExchangeSnapshotQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
    }),
  );
  const snapshotHistoryPrefetch = queryClient.prefetchQuery(
    getSnapshotHistoryQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      limit: HISTORY_LIMIT,
    }),
  );
  const [leagues] = await Promise.all([
    queryClient.fetchQuery(getLeaguesQueryOptions(params.realmId)),
    queryClient.fetchQuery(
      getReferenceCurrenciesQueryOptions(params.realmId, params.leagueId),
    ),
  ]);
  const league = leagues.find((league) => league.value === params.leagueId);

  if (!league) {
    throw new Response("Invalid league", { status: 404 });
  }

  await Promise.all([snapshotPrefetch, snapshotHistoryPrefetch]);

  return tableState;
}

export default function Exchange({ params, loaderData }: Route.ComponentProps) {
  const { league } = useLeagueContext();
  const { data: referenceCurrencies } = useSuspenseQuery(
    getReferenceCurrenciesQueryOptions(params.realmId, params.leagueId),
  );
  const baseCurrencyApiIds = getBaseCurrencyApiIds(referenceCurrencies);
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
  const pairsQuery = useQuery(
    getSnapshotPairsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      baseCurrencyApiIds,
    }),
  );

  return (
    <div className="flex flex-col gap-4 py-4">
      <ExchangeSummary league={league} snapshot={snapshot} />
      <MarketHistoryChart
        history={history.data}
        baseCurrencyText={history.baseCurrencyText || snapshot.baseCurrencyText}
      />
      <ExchangePairTable
        pairs={pairsQuery.data ?? []}
        tableState={loaderData}
        isLoading={pairsQuery.isPending}
        isError={pairsQuery.isError}
      />
    </div>
  );
}

function getBaseCurrencyApiIds(referenceCurrencies: LeagueCurrency[]) {
  return referenceCurrencies.map((currency) => currency.apiId);
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
