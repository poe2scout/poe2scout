import { useQuery, useSuspenseQuery } from "@tanstack/react-query";
import { useLocation, useNavigate, useSearchParams } from "react-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { BreadcrumbHandle } from "~/features/app-shell/components/header-breadcrumbs";
import { useLeagueContext } from "~/features/league/context";
import getLeaguesQueryOptions from "~/features/league/queries/leagues";
import { findLeagueByRouteId } from "~/features/league/route-id";
import getReferenceCurrenciesQueryOptions from "~/features/league/queries/reference-currencies";
import type { LeagueCurrency } from "~/features/league/types";
import { queryClient } from "~/shared/api/query-client";
import PairHistoryChart from "../components/pair-history-chart";
import { PAIR_HISTORY_METRIC_LABELS } from "../components/pair-history-metrics";
import { getPairHistoryQueryOptions } from "../queries/pair-history";
import { getSnapshotPairsQueryOptions } from "../queries/snapshot-pairs";
import type {
  ExchangePairHistoryDataKey,
  ExchangePairHistoryEntry,
  ExchangePairHistoryMetricKey,
  ExchangePairHistoryMetricOption,
  ExchangePairHistoryResponse,
  ExchangeSnapshotPair,
} from "../types";
import formatEpoch from "../utils/format-epoch";
import type { Route } from "./+types/pair-history";
import {
  formatTitle,
  getLeagueContextTitle,
  getPairTitleFallback,
} from "~/shared/meta/page-title";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => [
    {
      label: "Currency Exchange",
      to: `/${params.realmId}/${params.leagueId}/exchange`,
    },
    { label: "Pair" },
  ],
};

export function meta({ loaderData, matches, params }: Route.MetaArgs) {
  const pairTitle =
    loaderData?.pairTitle ??
    getPairTitleFallback(params.currencyOneItemId, params.currencyTwoItemId);
  const leagueContext = getLeagueContextTitle(matches);

  return [
    { title: formatTitle([`${pairTitle} Exchange History`, leagueContext]) },
  ];
}

const HISTORY_LIMIT = 24 * 14;
const DEFAULT_METRIC_ID = "currencyTwoData.valueTraded";

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  const currencyOneItemId = Number(params.currencyOneItemId);
  const currencyTwoItemId = Number(params.currencyTwoItemId);

  if (
    !Number.isInteger(currencyOneItemId) ||
    !Number.isInteger(currencyTwoItemId)
  ) {
    throw new Response("Invalid pair", { status: 404 });
  }

  const pairHistoryPrefetch = queryClient.prefetchQuery(
    getPairHistoryQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      currencyOneItemId,
      currencyTwoItemId,
      limit: HISTORY_LIMIT,
    }),
  );
  const [leagues, referenceCurrencies] = await Promise.all([
    queryClient.fetchQuery(getLeaguesQueryOptions(params.realmId)),
    queryClient.fetchQuery(
      getReferenceCurrenciesQueryOptions(params.realmId, params.leagueId),
    ),
  ]);
  const league = findLeagueByRouteId(leagues, params.leagueId);

  if (!league) {
    throw new Response("Invalid league", { status: 404 });
  }

  const baseCurrencyApiIds = getBaseCurrencyApiIds(referenceCurrencies);
  const snapshotPairs = await queryClient.fetchQuery(
    getSnapshotPairsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      baseCurrencyApiIds,
    }),
  );
  const pair = findPairByItems(
    snapshotPairs,
    currencyOneItemId,
    currencyTwoItemId,
  );
  const pairTitle = pair
    ? `${pair.currencyOne.text} / ${pair.currencyTwo.text}`
    : null;

  await pairHistoryPrefetch;

  return {
    currencyOneItemId,
    currencyTwoItemId,
    baseCurrencyApiIds,
    pairTitle,
  };
}

export default function PairHistory({
  params,
  loaderData,
}: Route.ComponentProps) {
  const { league, realm } = useLeagueContext();
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const locationPair = getStatePair(location.state);
  const { data: snapshotPairs } = useSuspenseQuery(
    getSnapshotPairsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
      baseCurrencyApiIds: loaderData.baseCurrencyApiIds,
    }),
  );
  const pair = useMemo(
    () =>
      locationPair ??
      findPairByItems(
        snapshotPairs,
        loaderData.currencyOneItemId,
        loaderData.currencyTwoItemId,
      ),
    [
      loaderData.currencyOneItemId,
      loaderData.currencyTwoItemId,
      locationPair,
      snapshotPairs,
    ],
  );
  const pairHistory = usePairHistory({
    realmApiId: realm.realmApiId,
    leagueName: league.shortName,
    currencyOneItemId: loaderData.currencyOneItemId,
    currencyTwoItemId: loaderData.currencyTwoItemId,
  });
  const baseCurrencyText =
    pairHistory.baseCurrencyText ||
    pair?.baseCurrencyText ||
    league.baseCurrencyText;
  const metricOptions = useMemo(
    () =>
      getMetricOptions({
        pair,
        currencyOneItemId: loaderData.currencyOneItemId,
        currencyTwoItemId: loaderData.currencyTwoItemId,
      }),
    [loaderData.currencyOneItemId, loaderData.currencyTwoItemId, pair],
  );
  const selectedMetricId = searchParams.get("metric") || DEFAULT_METRIC_ID;
  const selectedOption =
    metricOptions.find((option) => option.id === selectedMetricId) ??
    metricOptions[0];
  const latestEntry = pairHistory.history.at(-1);
  const backTo = useMemo(() => {
    const nextParams = new URLSearchParams(searchParams);
    nextParams.delete("metric");
    const query = nextParams.toString();

    return `/${params.realmId}/${params.leagueId}/exchange${query ? `?${query}` : ""}`;
  }, [params.leagueId, params.realmId, searchParams]);
  const lineUnit = getLineUnit(selectedOption, baseCurrencyText);
  const lineLabel = `${PAIR_HISTORY_METRIC_LABELS[selectedOption.metricKey]}${
    lineUnit ? ` (${lineUnit})` : ""
  }`;
  const histogramLabel = `Volume traded (${selectedOption.itemName})`;

  const setMetric = (metricId: string) => {
    const nextParams = new URLSearchParams(searchParams);
    nextParams.set("metric", metricId);
    setSearchParams(nextParams, {
      preventScrollReset: true,
      replace: true,
      state: location.state,
    });
  };
  const goBack = () => {
    if (isFromExchangeTable(location.state)) {
      navigate(-1);
      return;
    }

    navigate(backTo);
  };

  return (
    <section className="mt-4 overflow-hidden rounded-sm border border-secondary/35 bg-zinc-900 shadow-lg shadow-black/30">
      <header className="flex flex-col gap-4 border-b border-secondary/25 px-4 py-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={goBack}
            className="shrink-0 rounded-sm border border-secondary/35 px-3 py-2 text-sm text-white/80 transition hover:bg-secondary/20 hover:text-white focus:bg-secondary/25 focus:outline-none"
          >
            Back
          </button>
          <PairTitle
            pair={pair}
            currencyOneItemId={loaderData.currencyOneItemId}
            currencyTwoItemId={loaderData.currencyTwoItemId}
          />
        </div>
        {latestEntry && (
          <div className="text-sm text-white/50">
            Updated {formatEpoch(latestEntry.epoch)}
          </div>
        )}
      </header>

      {!pair && !pairHistory.isInitialLoading && (
        <div className="border-b border-secondary/25 bg-secondary/10 px-4 py-3 text-sm text-white/75">
          Pair is not present in the current snapshot. Showing history only.
        </div>
      )}

      <div className="flex flex-col gap-4 px-2 py-4 sm:px-4">
        <section className="rounded-sm border border-secondary/35 bg-zinc-900/40">
          <div className="flex flex-col gap-3 border-b border-secondary/25 p-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-lg font-semibold text-white">Pair History</h1>
              <p className="text-sm text-white/55">
                Compare price, value, volume, and stock metrics over time.
              </p>
            </div>
            <label className="flex items-center gap-2 text-sm text-white/70">
              <span>Metric</span>
              <select
                value={selectedOption.id}
                onChange={(event) => setMetric(event.currentTarget.value)}
                className="h-9 max-w-full rounded-sm border border-secondary/35 bg-zinc-900/40 px-2 text-white outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/25"
              >
                {metricOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="relative min-h-130 px-2 py-4 sm:px-4">
            <ChartState
              isLoading={pairHistory.isInitialLoading}
              isError={pairHistory.isError}
              isEmpty={pairHistory.history.length === 0}
            >
              <PairHistoryChart
                history={pairHistory.history}
                selectedOption={selectedOption}
                lineLabel={lineLabel}
                histogramLabel={histogramLabel}
                hasMore={pairHistory.hasMore}
                isLoadingMore={pairHistory.isLoadingMore}
                onLoadMore={pairHistory.loadMore}
              />
            </ChartState>
          </div>
        </section>
      </div>
    </section>
  );
}

function usePairHistory({
  realmApiId,
  leagueName,
  currencyOneItemId,
  currencyTwoItemId,
}: {
  realmApiId: string;
  leagueName: string;
  currencyOneItemId: number;
  currencyTwoItemId: number;
}) {
  const [history, setHistory] = useState<ExchangePairHistoryEntry[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [oldestEpoch, setOldestEpoch] = useState<number | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [baseCurrencyText, setBaseCurrencyText] = useState("");

  useEffect(() => {
    setHistory([]);
    setHasMore(true);
    setOldestEpoch(null);
    setBaseCurrencyText("");
  }, [currencyOneItemId, currencyTwoItemId, leagueName, realmApiId]);

  const query = useQuery(
    getPairHistoryQueryOptions({
      realmApiId,
      leagueName,
      currencyOneItemId,
      currencyTwoItemId,
      limit: HISTORY_LIMIT,
    }),
  );

  useEffect(() => {
    if (!query.data) return;

    const ordered = [...query.data.history].sort((a, b) => a.epoch - b.epoch);
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
        getPairHistoryQueryOptions({
          realmApiId,
          leagueName,
          currencyOneItemId,
          currencyTwoItemId,
          limit: HISTORY_LIMIT,
          endEpoch: oldestEpoch,
        }),
      )) as ExchangePairHistoryResponse;
      const ordered = [...data.history].sort((a, b) => a.epoch - b.epoch);

      setHistory((current) => prependUniqueHistory(current, ordered));
      setHasMore(data.hasMore);
      setOldestEpoch(ordered[0]?.epoch ?? oldestEpoch);
      setBaseCurrencyText(data.baseCurrencyText);
    } finally {
      setIsLoadingMore(false);
    }
  }, [
    currencyOneItemId,
    currencyTwoItemId,
    hasMore,
    isLoadingMore,
    leagueName,
    oldestEpoch,
    realmApiId,
  ]);

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

function ChartState({
  isLoading,
  isError,
  isEmpty,
  children,
}: {
  isLoading: boolean;
  isError: boolean;
  isEmpty: boolean;
  children: React.ReactNode;
}) {
  if (isLoading) {
    return <ChartMessage>Loading pair history...</ChartMessage>;
  }

  if (isError) {
    return <ChartMessage>Failed to load pair history.</ChartMessage>;
  }

  if (isEmpty) {
    return <ChartMessage>No pair history is available.</ChartMessage>;
  }

  return children;
}

function ChartMessage({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-125 items-center justify-center text-sm text-white/60">
      {children}
    </div>
  );
}

function PairTitle({
  pair,
  currencyOneItemId,
  currencyTwoItemId,
}: {
  pair: ExchangeSnapshotPair | null;
  currencyOneItemId: number;
  currencyTwoItemId: number;
}) {
  if (!pair) {
    return (
      <div className="min-w-0">
        <h1 className="truncate text-lg font-semibold text-white">
          Pair {currencyOneItemId} / {currencyTwoItemId}
        </h1>
        <p className="text-sm text-white/50">Historical exchange metrics</p>
      </div>
    );
  }

  return (
    <div className="flex min-w-0 flex-wrap items-center gap-2">
      <CurrencyName item={pair.currencyOne} />
      <span className="text-white/35">/</span>
      <CurrencyName item={pair.currencyTwo} />
    </div>
  );
}

function CurrencyName({ item }: { item: ExchangeSnapshotPair["currencyOne"] }) {
  return (
    <span className="inline-flex min-w-0 items-center gap-2">
      {item.iconUrl && (
        <img src={item.iconUrl} alt="" className="h-10 w-10 object-contain" />
      )}
      <span className="truncate text-lg font-semibold text-white">
        {item.text}
      </span>
    </span>
  );
}

function getMetricOptions({
  pair,
  currencyOneItemId,
  currencyTwoItemId,
}: {
  pair: ExchangeSnapshotPair | null;
  currencyOneItemId: number;
  currencyTwoItemId: number;
}): ExchangePairHistoryMetricOption[] {
  const defaultNames = {
    currencyOneData: `Item ${currencyOneItemId}`,
    currencyTwoData: `Item ${currencyTwoItemId}`,
  } as const;
  const sources: Array<{ key: ExchangePairHistoryDataKey; name: string }> = [
    {
      key: "currencyTwoData",
      name: pair?.currencyTwo.text ?? defaultNames.currencyTwoData,
    },
    {
      key: "currencyOneData",
      name: pair?.currencyOne.text ?? defaultNames.currencyOneData,
    },
  ];
  const metricOrder: ExchangePairHistoryMetricKey[] = [
    "pairPrice",
    "valueTraded",
    "volumeTraded",
    "stockValue",
    "highestStock",
  ];

  return sources.flatMap((source) =>
    metricOrder.map((metricKey) => ({
      id: `${source.key}.${metricKey}`,
      dataKey: source.key,
      metricKey,
      label: `${PAIR_HISTORY_METRIC_LABELS[metricKey]} (${source.name})`,
      itemName: source.name,
      counterpartName:
        source.key === "currencyTwoData"
          ? (pair?.currencyOne.text ?? defaultNames.currencyOneData)
          : (pair?.currencyTwo.text ?? defaultNames.currencyTwoData),
    })),
  );
}

function getLineUnit(
  option: ExchangePairHistoryMetricOption,
  baseCurrencyText: string,
) {
  switch (option.metricKey) {
    case "valueTraded":
    case "stockValue":
      return baseCurrencyText;
    case "volumeTraded":
    case "highestStock":
      return option.itemName;
    case "pairPrice":
    default:
      return option.counterpartName;
  }
}

function findPairByItems(
  pairs: ExchangeSnapshotPair[],
  currencyOneItemId: number,
  currencyTwoItemId: number,
) {
  return (
    pairs.find((candidate) => {
      const itemIds = [
        candidate.currencyOne.itemId,
        candidate.currencyTwo.itemId,
      ];
      return (
        itemIds.includes(currencyOneItemId) &&
        itemIds.includes(currencyTwoItemId)
      );
    }) ?? null
  );
}

function prependUniqueHistory(
  current: ExchangePairHistoryEntry[],
  older: ExchangePairHistoryEntry[],
) {
  const currentEpochs = new Set(current.map((entry) => entry.epoch));
  return [
    ...older.filter((entry) => !currentEpochs.has(entry.epoch)),
    ...current,
  ];
}

function getBaseCurrencyApiIds(referenceCurrencies: LeagueCurrency[]) {
  return referenceCurrencies.map((currency) => currency.apiId);
}

function getStatePair(state: unknown) {
  if (!state || typeof state !== "object" || !("pair" in state)) {
    return null;
  }

  const pair = (state as { pair?: unknown }).pair;
  if (!pair || typeof pair !== "object" || !("currencyOne" in pair)) {
    return null;
  }

  return pair as ExchangeSnapshotPair;
}

function isFromExchangeTable(state: unknown) {
  return (
    state !== null &&
    typeof state === "object" &&
    "fromExchangeTable" in state &&
    (state as { fromExchangeTable?: unknown }).fromExchangeTable === true
  );
}
