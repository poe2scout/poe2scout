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
  ExchangeSnapshot,
  SnapshotHistoryResponse,
  ExchangeTableState,
} from "~/features/exchange/types";
import { useQuery, useSuspenseQuery } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";
import getNumberNonZero from "~/shared/utils/get-number-non-zero";
import { getNextHourEndEpoch } from "~/shared/utils/chart-cursor";
import getLeaguesQueryOptions from "~/features/league/queries/leagues";
import { findLeagueByRouteId } from "~/features/league/route-id";
import getReferenceCurrenciesQueryOptions from "~/features/league/queries/reference-currencies";
import type { LeagueCurrency } from "~/features/league/types";
import {
  formatTitle,
  getLeagueContextTitle,
} from "~/shared/meta/page-title";
import ResponsiveAdLayout from "~/shared/components/ads/responsive-ad-layout";

export const handle: BreadcrumbHandle = {
  breadcrumb: () => ({ label: "Currency Exchange" }),
};

export function meta({ matches }: Route.MetaArgs) {
  const leagueContext = getLeagueContextTitle(matches);

  return [{ title: formatTitle(["Currency Exchange", leagueContext]) }];
}

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
  const initialEndEpoch = getNextHourEndEpoch();
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
      endEpoch: initialEndEpoch,
    }),
  );
  const [leagues] = await Promise.all([
    queryClient.fetchQuery(getLeaguesQueryOptions(params.realmId)),
    queryClient.fetchQuery(
      getReferenceCurrenciesQueryOptions(params.realmId, params.leagueId),
    ),
  ]);
  const league = findLeagueByRouteId(leagues, params.leagueId);

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
  const snapshotHistory = useSnapshotHistory({
    realmApiId: params.realmId,
    leagueName: params.leagueId,
  });
  const pairsQuery = useQuery(
    getSnapshotPairsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      baseCurrencyApiIds,
    }),
  );

  return (
    <ResponsiveAdLayout>
      <div className="flex flex-col gap-4 py-4">
        <ExchangeSummary league={league} snapshot={snapshot} />
        <MarketHistoryChart
          history={snapshotHistory.history}
          baseCurrencyText={
            snapshotHistory.baseCurrencyText || snapshot.baseCurrencyText
          }
          hasMore={snapshotHistory.hasMore}
          isLoading={snapshotHistory.isInitialLoading}
          isError={snapshotHistory.isError}
          isLoadingMore={snapshotHistory.isLoadingMore}
          onLoadMore={snapshotHistory.loadMore}
        />
        <ExchangePairTable
          pairs={pairsQuery.data ?? []}
          tableState={loaderData}
          isLoading={pairsQuery.isPending}
          isError={pairsQuery.isError}
        />
      </div>
    </ResponsiveAdLayout>
  );
}

function useSnapshotHistory({
  realmApiId,
  leagueName,
}: {
  realmApiId: string;
  leagueName: string;
}) {
  const [history, setHistory] = useState<ExchangeSnapshot[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [oldestEpoch, setOldestEpoch] = useState<number | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [baseCurrencyText, setBaseCurrencyText] = useState("");
  const [initialEndEpoch, setInitialEndEpoch] = useState(() =>
    getNextHourEndEpoch(),
  );

  useEffect(() => {
    setHistory([]);
    setHasMore(true);
    setOldestEpoch(null);
    setBaseCurrencyText("");
    setInitialEndEpoch(getNextHourEndEpoch());
  }, [leagueName, realmApiId]);

  const query = useQuery(
    getSnapshotHistoryQueryOptions({
      realmApiId,
      leagueName,
      limit: HISTORY_LIMIT,
      endEpoch: initialEndEpoch,
    }),
  );

  useEffect(() => {
    if (!query.data) return;

    const ordered = [...query.data.data].sort((a, b) => a.epoch - b.epoch);
    setHistory(ordered);
    setHasMore(query.data.hasMore);
    setOldestEpoch(ordered[0]?.epoch ?? null);
    setBaseCurrencyText(query.data.baseCurrencyText);
  }, [query.data]);

  const loadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore || !oldestEpoch) return;

    setIsLoadingMore(true);
    try {
      const data = (await queryClient.fetchQuery(
        getSnapshotHistoryQueryOptions({
          realmApiId,
          leagueName,
          limit: HISTORY_LIMIT,
          endEpoch: oldestEpoch,
        }),
      )) as SnapshotHistoryResponse;
      const ordered = [...data.data].sort((a, b) => a.epoch - b.epoch);

      setHistory((current) => prependUniqueSnapshotHistory(current, ordered));
      setHasMore(data.hasMore);
      setOldestEpoch(ordered[0]?.epoch ?? oldestEpoch);
      setBaseCurrencyText(data.baseCurrencyText);
    } finally {
      setIsLoadingMore(false);
    }
  }, [hasMore, isLoadingMore, leagueName, oldestEpoch, realmApiId]);

  return {
    history,
    hasMore,
    baseCurrencyText,
    isInitialLoading: query.isPending,
    isError: query.isError,
    isLoadingMore,
    loadMore,
  };
}

function prependUniqueSnapshotHistory(
  current: ExchangeSnapshot[],
  next: ExchangeSnapshot[],
) {
  const seen = new Set(current.map((entry) => entry.epoch));
  const uniqueNext = next.filter((entry) => !seen.has(entry.epoch));

  return [...uniqueNext, ...current].sort((a, b) => a.epoch - b.epoch);
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
