import { useQuery } from "@tanstack/react-query";
import { useLocation, useNavigate } from "react-router";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";

import type { League, LeagueCurrency, Realm } from "~/features/league/types";
import { queryClient } from "~/shared/api/query-client";
import SelectField from "~/shared/components/select";
import type {
  DailyStatEntry,
  EconomyItem,
  ItemDailyStatsHistoryResponse,
  ItemHistoryResponse,
  ItemSummary,
  PriceLogEntry,
} from "../types";
import {
  getItemDailyStatsHistoryQueryOptions,
  getItemHistoryQueryOptions,
} from "../queries/item-history";
import {
  type ChartMode,
  type DailyChartData,
  type DailyLegendData,
  type RawChartData,
  type RawLegendData,
} from "./item-history-charts";
import { RawPriceChart } from "./item-history-raw-chart";
import { DailyStatsChart } from "./item-history-daily-chart";
import { formatEpoch, formatFixed, formatInteger, toEpoch } from "../utils";

const INITIAL_RAW_LOG_COUNT = 14 * 24;
const DAILY_DAY_COUNT = 90;

export default function ItemDetail({
  item,
  chartMode,
  realm,
  league,
  referenceCurrencies,
  referenceCurrency,
  backTo,
  setDetailParam,
}: {
  routeKind: "currencies" | "uniques";
  item: ItemSummary;
  chartMode: ChartMode;
  realm: Realm;
  league: League;
  referenceCurrencies: LeagueCurrency[];
  referenceCurrency: string;
  backTo: string;
  setDetailParam: (key: string, value: string) => void;
}) {
  const location = useLocation();
  const navigate = useNavigate();
  const displayItem = getDisplayItem(item, item.itemId);
  const referenceCurrencyOptions =
    getReferenceCurrencyOptions(referenceCurrencies);
  const selectedReferenceCurrency = getValidReferenceCurrency(
    referenceCurrency,
    league,
    referenceCurrencies,
  );

  const rawHistory = useRawItemHistory({
    enabled: chartMode === "raw" && Number.isFinite(item.itemId),
    realmApiId: realm.realmApiId,
    leagueName: league.shortName,
    itemId: item.itemId,
    referenceCurrency: selectedReferenceCurrency,
  });

  const dailyHistory = useDailyItemHistory({
    enabled: chartMode === "daily" && Number.isFinite(item.itemId),
    realmApiId: realm.realmApiId,
    leagueName: league.shortName,
    itemId: item.itemId,
  });

  const rawChartData = useMemo(
    () => toRawChartData(rawHistory.history),
    [rawHistory.history],
  );
  const dailyChartData = useMemo(
    () => toDailyChartData(dailyHistory.dailyStats),
    [dailyHistory.dailyStats],
  );

  const [rawLegendData, setRawLegendData] = useState<RawLegendData>({});
  const [dailyLegendData, setDailyLegendData] = useState<DailyLegendData>({});
  const goBack = () => {
    if (isFromEconomyTable(location.state)) {
      navigate(-1);
      return;
    }

    navigate(backTo);
  };

  return (
    <section className="overflow-hidden rounded-sm border border-secondary/35 bg-zinc-900 shadow-lg shadow-black/30">
      <header className="flex flex-col gap-4 border-b border-secondary/25 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={goBack}
            className="shrink-0 rounded-sm border border-secondary/35 px-3 py-2 text-sm text-white/80 transition hover:bg-secondary/20 hover:text-white focus:bg-secondary/25 focus:outline-none"
          >
            Back
          </button>
          <img
            src={displayItem.iconUrl ?? undefined}
            alt=""
            className="h-10 w-10 shrink-0 object-contain"
          />
          <div className="min-w-0">
            <h1
              className={`truncate text-lg font-semibold ${displayItem.isUnique ? "text-amber-500" : "text-white"}`}
            >
              {displayItem.title}
            </h1>
            {displayItem.subtitle && (
              <p className="truncate text-sm text-white/50">
                {displayItem.subtitle}
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
          <div className="grid grid-cols-2 overflow-hidden rounded-sm border border-secondary/35 text-sm">
            <button
              type="button"
              aria-pressed={chartMode === "raw"}
              onClick={() => setDetailParam("chart", "raw")}
              className={`px-4 py-2 transition ${chartMode === "raw" ? "bg-secondary/30 text-white" : "text-white/70 hover:bg-secondary/15"}`}
            >
              Raw
            </button>
            <button
              type="button"
              aria-pressed={chartMode === "daily"}
              onClick={() => setDetailParam("chart", "daily")}
              className={`border-l border-secondary/25 px-4 py-2 transition ${chartMode === "daily" ? "bg-secondary/30 text-white" : "text-white/70 hover:bg-secondary/15"}`}
            >
              Daily
            </button>
          </div>

          {chartMode === "raw" && (
            <SelectField
              label="Currency"
              value={selectedReferenceCurrency}
              onChange={(event) =>
                setDetailParam("referenceCurrency", event.currentTarget.value)
              }
              className="flex items-center gap-2 text-sm text-white/70"
              labelClassName=""
              wrapperClassName="h-9 bg-zinc-900/60 px-2"
            >
              {referenceCurrencyOptions.map((option) => (
                <option key={option.apiId} value={option.apiId}>
                  {option.label}
                </option>
              ))}
            </SelectField>
          )}
        </div>
      </header>

      <div className="relative min-h-130 px-2 py-4 sm:px-4">
        {chartMode === "raw" ? (
          <ChartState
            isLoading={rawHistory.isInitialLoading}
            isError={rawHistory.isError}
            isEmpty={rawHistory.history.length === 0}
          >
            <RawLegend
              data={rawLegendData}
              referenceCurrency={getCurrencyLabel(
                selectedReferenceCurrency,
                referenceCurrencies,
              )}
            />
            <RawPriceChart
              chartData={rawChartData}
              hasMore={rawHistory.hasMore}
              isLoadingMore={rawHistory.isLoadingMore}
              onLoadMore={rawHistory.loadMore}
              onLegendDataChange={setRawLegendData}
              height={500}
            />
          </ChartState>
        ) : (
          <ChartState
            isLoading={dailyHistory.isInitialLoading}
            isError={dailyHistory.isError}
            isEmpty={dailyHistory.dailyStats.length === 0}
          >
            <DailyLegend
              data={dailyLegendData}
              currency={
                dailyHistory.baseCurrencyText ?? league.baseCurrencyText
              }
            />
            <DailyStatsChart
              chartData={dailyChartData}
              hasMore={dailyHistory.hasMore}
              isLoadingMore={dailyHistory.isLoadingMore}
              onLoadMore={dailyHistory.loadMore}
              onLegendDataChange={setDailyLegendData}
              height={500}
            />
          </ChartState>
        )}
      </div>
    </section>
  );
}

function useRawItemHistory({
  enabled,
  realmApiId,
  leagueName,
  itemId,
  referenceCurrency,
}: {
  enabled: boolean;
  realmApiId: string;
  leagueName: string;
  itemId: number;
  referenceCurrency: string;
}) {
  const [history, setHistory] = useState<PriceLogEntry[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [oldestTimestamp, setOldestTimestamp] = useState<string | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [cursor, setCursor] = useState(() => new Date().toISOString());
  const didMountRef = useRef(false);
  const nextLogCountRef = useRef(INITIAL_RAW_LOG_COUNT * 2);

  useEffect(() => {
    if (!didMountRef.current) {
      didMountRef.current = true;
      return;
    }

    setHistory([]);
    setHasMore(true);
    setOldestTimestamp(null);
    setCursor(new Date().toISOString());
    nextLogCountRef.current = INITIAL_RAW_LOG_COUNT * 2;
  }, [itemId, leagueName, realmApiId, referenceCurrency]);

  const query = useQuery({
    ...getItemHistoryQueryOptions({
      realmApiId,
      leagueName,
      itemId,
      logCount: INITIAL_RAW_LOG_COUNT,
      referenceCurrency,
      endTime: cursor,
    }),
    enabled,
  });

  useEffect(() => {
    if (!query.data) return;

    const ordered = [...query.data.priceHistory].reverse();
    setHistory(ordered);
    setHasMore(query.data.hasMore);
    setOldestTimestamp(ordered[0]?.time ?? null);
  }, [query.data]);

  const loadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore || !oldestTimestamp) return;

    setIsLoadingMore(true);
    try {
      const data = (await queryClient.fetchQuery(
        getItemHistoryQueryOptions({
          realmApiId,
          leagueName,
          itemId,
          logCount: nextLogCountRef.current,
          referenceCurrency,
          endTime: oldestTimestamp,
        }),
      )) as ItemHistoryResponse;
      const ordered = [...data.priceHistory].reverse();
      setHistory((current) => prependUniqueHistory(current, ordered));
      setHasMore(data.hasMore);
      setOldestTimestamp(ordered[0]?.time ?? oldestTimestamp);
      nextLogCountRef.current = nextLogCountRef.current * 2;
    } finally {
      setIsLoadingMore(false);
    }
  }, [
    hasMore,
    isLoadingMore,
    itemId,
    leagueName,
    oldestTimestamp,
    realmApiId,
    referenceCurrency,
  ]);

  return {
    history,
    hasMore,
    isInitialLoading: enabled && query.isPending,
    isError: query.isError,
    isLoadingMore,
    loadMore,
  };
}

function useDailyItemHistory({
  enabled,
  realmApiId,
  leagueName,
  itemId,
}: {
  enabled: boolean;
  realmApiId: string;
  leagueName: string;
  itemId: number;
}) {
  const [dailyStats, setDailyStats] = useState<DailyStatEntry[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [oldestDate, setOldestDate] = useState<string | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [baseCurrencyText, setBaseCurrencyText] = useState<string | null>(null);

  useEffect(() => {
    setDailyStats([]);
    setHasMore(true);
    setOldestDate(null);
    setBaseCurrencyText(null);
  }, [itemId, leagueName, realmApiId]);

  const query = useQuery({
    ...getItemDailyStatsHistoryQueryOptions({
      realmApiId,
      leagueName,
      itemId,
      dayCount: DAILY_DAY_COUNT,
    }),
    enabled,
  });

  useEffect(() => {
    if (!query.data) return;

    setDailyStats(query.data.dailyStats);
    setHasMore(query.data.hasMore);
    setOldestDate(query.data.dailyStats[0]?.time ?? null);
    setBaseCurrencyText(query.data.baseCurrencyText);
  }, [query.data]);

  const loadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore || !oldestDate) return;

    setIsLoadingMore(true);
    try {
      const data = (await queryClient.fetchQuery(
        getItemDailyStatsHistoryQueryOptions({
          realmApiId,
          leagueName,
          itemId,
          dayCount: DAILY_DAY_COUNT,
          endDate: oldestDate,
        }),
      )) as ItemDailyStatsHistoryResponse;
      setDailyStats((current) =>
        prependUniqueDailyStats(current, data.dailyStats),
      );
      setHasMore(data.hasMore);
      setOldestDate(data.dailyStats[0]?.time ?? oldestDate);
      setBaseCurrencyText(data.baseCurrencyText);
    } finally {
      setIsLoadingMore(false);
    }
  }, [hasMore, isLoadingMore, itemId, leagueName, oldestDate, realmApiId]);

  return {
    dailyStats,
    hasMore,
    baseCurrencyText,
    isInitialLoading: enabled && query.isPending,
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
  children: ReactNode;
}) {
  if (isLoading) {
    return <ChartMessage>Loading price history...</ChartMessage>;
  }

  if (isError) {
    return <ChartMessage>Failed to load price history.</ChartMessage>;
  }

  if (isEmpty) {
    return <ChartMessage>No price history is available.</ChartMessage>;
  }

  return <div className="relative h-125 w-full">{children}</div>;
}

function ChartMessage({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-125 items-center justify-center text-sm text-white/60">
      {children}
    </div>
  );
}

function RawLegend({
  data,
  referenceCurrency,
}: {
  data: RawLegendData;
  referenceCurrency: string;
}) {
  if (
    data.price === undefined &&
    data.volume === undefined &&
    data.time === undefined
  ) {
    return null;
  }

  return (
    <div className="pointer-events-none absolute top-3 left-16 z-10 max-w-[calc(100%-4rem)] text-sm text-white">
      {data.price !== undefined && (
        <div>
          <span className="text-white/55">Price: </span>
          <strong>{formatFixed(data.price)}</strong>
          <span className="text-white/55"> {referenceCurrency}</span>
        </div>
      )}
      {data.volume !== undefined && (
        <div>
          <span className="text-white/55">Volume: </span>
          <strong>{formatInteger(data.volume)}</strong>
        </div>
      )}
      {data.time !== undefined && (
        <div className="mt-1 text-white/55">{formatEpoch(data.time)}</div>
      )}
    </div>
  );
}

function DailyLegend({
  data,
  currency,
}: {
  data: DailyLegendData;
  currency: string;
}) {
  if (
    data.open === undefined &&
    data.high === undefined &&
    data.low === undefined &&
    data.close === undefined &&
    data.volume === undefined &&
    data.time === undefined
  ) {
    return null;
  }

  return (
    <div className="pointer-events-none absolute top-3 left-16 z-10 max-w-[calc(100%-4rem)] text-sm text-white">
      {data.time && <div className="mb-1 text-white/55">{data.time}</div>}
      {data.open !== undefined &&
        data.high !== undefined &&
        data.low !== undefined &&
        data.close !== undefined && (
          <div>
            <span className="text-white/55">O: </span>
            <strong>{formatFixed(data.open)}</strong>
            <span className="text-white/55"> H: </span>
            <strong>{formatFixed(data.high)}</strong>
            <span className="text-white/55"> L: </span>
            <strong>{formatFixed(data.low)}</strong>
            <span className="text-white/55"> C: </span>
            <strong>{formatFixed(data.close)}</strong>
            <span className="text-white/55"> {currency}</span>
          </div>
        )}
      {data.volume !== undefined && (
        <div>
          <span className="text-white/55">Volume: </span>
          <strong>{formatInteger(data.volume)}</strong>
        </div>
      )}
    </div>
  );
}

function toRawChartData(history: PriceLogEntry[]): RawChartData {
  return {
    lineData: history.map((entry) => ({
      time: toEpoch(entry.time),
      value: entry.price,
    })),
    histogramData: history.map((entry) => ({
      time: toEpoch(entry.time),
      value: entry.quantity,
    })),
  };
}

function toDailyChartData(dailyStats: DailyStatEntry[]): DailyChartData {
  return {
    candlestickData: dailyStats.map((entry) => ({
      time: entry.time,
      open: entry.open,
      high: entry.high,
      low: entry.low,
      close: entry.close,
    })),
    histogramData: dailyStats.map((entry) => ({
      time: entry.time,
      value: entry.volume,
    })),
  };
}

function prependUniqueHistory(
  current: PriceLogEntry[],
  older: PriceLogEntry[],
) {
  const currentTimes = new Set(current.map((entry) => entry.time));
  return [
    ...older.filter((entry) => !currentTimes.has(entry.time)),
    ...current,
  ];
}

function prependUniqueDailyStats(
  current: DailyStatEntry[],
  older: DailyStatEntry[],
) {
  const currentTimes = new Set(current.map((entry) => entry.time));
  return [
    ...older.filter((entry) => !currentTimes.has(entry.time)),
    ...current,
  ];
}

function getStateItem(state: unknown): EconomyItem | null {
  if (!state || typeof state !== "object" || !("item" in state)) {
    return null;
  }

  const item = (state as { item?: unknown }).item;
  if (!item || typeof item !== "object" || !("itemId" in item)) {
    return null;
  }

  return item as EconomyItem;
}

function isFromEconomyTable(state: unknown) {
  return (
    state !== null &&
    typeof state === "object" &&
    "fromEconomyTable" in state &&
    (state as { fromEconomyTable?: unknown }).fromEconomyTable === true
  );
}

function getDisplayItem(
  item: EconomyItem | ItemSummary | undefined,
  itemId: number,
) {
  if (!item) {
    return {
      title: `Item ${itemId}`,
      subtitle: null,
      iconUrl: null,
      isUnique: false,
    };
  }

  if ("uniqueItemId" in item) {
    return {
      title: item.name,
      subtitle: getMetadataSubtitle(item.itemMetadata) ?? item.type,
      iconUrl: item.iconUrl,
      isUnique: true,
    };
  }

  if ("currencyItemId" in item) {
    return {
      title: item.text,
      subtitle: getMetadataSubtitle(item.itemMetadata),
      iconUrl: item.iconUrl,
      isUnique: false,
    };
  }

  return {
    title: item.name ?? item.text,
    subtitle: item.type ?? item.categoryApiId,
    iconUrl: item.iconUrl,
    isUnique: Boolean(item.name),
  };
}

function getMetadataSubtitle(
  metadata: EconomyItem["itemMetadata"],
): string | null {
  if (!metadata) return null;
  return metadata.baseType ?? metadata.name ?? null;
}

function getReferenceCurrencyOptions(referenceCurrencies: LeagueCurrency[]) {
  return referenceCurrencies.map((currency) => ({
    apiId: currency.apiId,
    label: currency.text,
  }));
}

function getValidReferenceCurrency(
  apiId: string,
  league: League,
  referenceCurrencies: LeagueCurrency[],
) {
  return getReferenceCurrencyOptions(referenceCurrencies).some(
    (option) => option.apiId === apiId,
  )
    ? apiId
    : league.defaultCurrency.apiId;
}

function getCurrencyLabel(
  apiId: string,
  referenceCurrencies: LeagueCurrency[],
) {
  return (
    getReferenceCurrencyOptions(referenceCurrencies).find(
      (option) => option.apiId === apiId,
    )?.label ?? apiId
  );
}
