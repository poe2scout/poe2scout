import { queryOptions } from "@tanstack/react-query";
import type {
  ExchangeCurrencyItem,
  ExchangePairData,
  ExchangeSnapshot,
  ExchangeSnapshotPair,
  SnapshotHistoryResponse,
} from "../types";
import fetchRoute from "~/shared/api/fetch-route";
import toQueryString from "~/shared/utils/to-query-string";

export type NumberLike = string | number | null | undefined;

export type ExchangeSnapshotPayload = {
  epoch: number;
  volume: NumberLike;
  marketCap: NumberLike;
  baseCurrencyApiId: string;
  baseCurrencyText: string;
};

export type ExchangePairDataPayload = {
  valueTraded?: NumberLike;
  valuetraded?: NumberLike;
  relativePrice?: NumberLike;
  stockValue?: NumberLike;
  volumeTraded?: NumberLike;
  highestStock?: NumberLike;
};

export type ExchangeSnapshotPairPayload = {
  currencyExchangeSnapshotPairId: number;
  currencyExchangeSnapshotId: number;
  volume: NumberLike;
  baseCurrencyApiId: string;
  baseCurrencyText: string;
  currencyOne: ExchangeCurrencyItem;
  currencyTwo: ExchangeCurrencyItem;
  currencyOneData: ExchangePairDataPayload;
  currencyTwoData: ExchangePairDataPayload;
};

type SnapshotHistoryPayload = {
  data?: ExchangeSnapshotPayload[];
  meta?: {
    hasMore?: boolean;
  };
  baseCurrencyApiId?: string;
  baseCurrencyText?: string;
};

const SNAPSHOT_STALE_TIME_MS = 60 * 1000;
const SNAPSHOT_PAIRS_STALE_TIME_MS = 10 * 60 * 1000;

function toNumber(value: NumberLike) {
  if (value === null || value === undefined) {
    return 0;
  }

  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function normalizeSnapshot(
  snapshot: ExchangeSnapshotPayload,
): ExchangeSnapshot {
  return {
    epoch: snapshot.epoch,
    volume: toNumber(snapshot.volume),
    marketCap: toNumber(snapshot.marketCap),
    baseCurrencyApiId: snapshot.baseCurrencyApiId,
    baseCurrencyText: snapshot.baseCurrencyText,
  };
}

function normalizePairData(data: ExchangePairDataPayload): ExchangePairData {
  const volumeTraded = toNumber(data.volumeTraded);
  const relativePrice = toNumber(data.relativePrice);
  const explicitValue = toNumber(data.valueTraded ?? data.valuetraded);
  const derivedValue = relativePrice * volumeTraded;

  return {
    valueTraded: derivedValue > 0 ? derivedValue : explicitValue,
    relativePrice,
    stockValue: toNumber(data.stockValue),
    volumeTraded,
    highestStock: toNumber(data.highestStock),
    pairPrice: 0,
  };
}

function computePairPrices(
  first: ExchangePairData,
  second: ExchangePairData,
): [ExchangePairData, ExchangePairData] {
  const safeDivide = (numerator: number, denominator: number) =>
    denominator > 0 ? numerator / denominator : 0;

  return [
    {
      ...first,
      pairPrice: safeDivide(second.volumeTraded, first.volumeTraded),
    },
    {
      ...second,
      pairPrice: safeDivide(first.volumeTraded, second.volumeTraded),
    },
  ];
}

function isBaseCurrency(
  item: ExchangeCurrencyItem,
  baseCurrencyApiIds: Set<string>,
) {
  return baseCurrencyApiIds.has(item.apiId);
}

function buildSnapshotPair(
  row: ExchangeSnapshotPairPayload,
  currencyOne: ExchangeCurrencyItem,
  currencyTwo: ExchangeCurrencyItem,
  currencyOneData: ExchangePairData,
  currencyTwoData: ExchangePairData,
): ExchangeSnapshotPair {
  return {
    currencyExchangeSnapshotPairId: row.currencyExchangeSnapshotPairId,
    currencyExchangeSnapshotId: row.currencyExchangeSnapshotId,
    volume: toNumber(row.volume),
    baseCurrencyApiId: row.baseCurrencyApiId,
    baseCurrencyText: row.baseCurrencyText,
    currencyOne,
    currencyTwo,
    currencyOneData,
    currencyTwoData,
  };
}

export function normalizeSnapshotPair(
  row: ExchangeSnapshotPairPayload,
  baseCurrencyApiIds: Set<string>,
): ExchangeSnapshotPair {
  const currencyOneData = normalizePairData(row.currencyOneData);
  const currencyTwoData = normalizePairData(row.currencyTwoData);
  const areBothCurrencyBases =
    isBaseCurrency(row.currencyOne, baseCurrencyApiIds) &&
    isBaseCurrency(row.currencyTwo, baseCurrencyApiIds);

  if (areBothCurrencyBases) {
    const isCorrectOrder =
      currencyOneData.volumeTraded <= currencyTwoData.volumeTraded;
    const [firstWithPrice, secondWithPrice] = computePairPrices(
      isCorrectOrder ? currencyOneData : currencyTwoData,
      isCorrectOrder ? currencyTwoData : currencyOneData,
    );

    return buildSnapshotPair(
      row,
      isCorrectOrder ? row.currencyOne : row.currencyTwo,
      isCorrectOrder ? row.currencyTwo : row.currencyOne,
      firstWithPrice,
      secondWithPrice,
    );
  }

  if (!isBaseCurrency(row.currencyOne, baseCurrencyApiIds)) {
    const [firstWithPrice, secondWithPrice] = computePairPrices(
      currencyOneData,
      currencyTwoData,
    );

    return buildSnapshotPair(
      row,
      row.currencyOne,
      row.currencyTwo,
      firstWithPrice,
      secondWithPrice,
    );
  }

  const [firstWithPrice, secondWithPrice] = computePairPrices(
    currencyTwoData,
    currencyOneData,
  );

  return buildSnapshotPair(
    row,
    row.currencyTwo,
    row.currencyOne,
    firstWithPrice,
    secondWithPrice,
  );
}

export function getExchangeSnapshotQueryOptions({
  realmApiId,
  leagueName,
}: {
  realmApiId: string;
  leagueName: string;
}) {
  return queryOptions({
    queryKey: ["exchange", "snapshot", { realmApiId, leagueName }],
    staleTime: SNAPSHOT_STALE_TIME_MS,
    queryFn: async () => {
      const payload = await fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/ExchangeSnapshot`,
      );

      return normalizeSnapshot(payload as ExchangeSnapshotPayload);
    },
  });
}

export function getSnapshotHistoryQueryOptions({
  realmApiId,
  leagueName,
  limit,
}: {
  realmApiId: string;
  leagueName: string;
  limit: number;
}) {
  return queryOptions({
    queryKey: [
      "exchange",
      "snapshot-history",
      { realmApiId, leagueName, limit },
    ],
    staleTime: SNAPSHOT_STALE_TIME_MS,
    queryFn: async (): Promise<SnapshotHistoryResponse> => {
      const query = toQueryString({ Limit: limit });
      const payload = (await fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/SnapshotHistory${query}`,
      )) as SnapshotHistoryPayload;

      return {
        data: (payload.data ?? []).map(normalizeSnapshot),
        hasMore: Boolean(payload.meta?.hasMore),
        baseCurrencyApiId: payload.baseCurrencyApiId ?? "",
        baseCurrencyText: payload.baseCurrencyText ?? "",
      };
    },
  });
}

export function getSnapshotPairsQueryOptions({
  realmApiId,
  leagueName,
  baseCurrencyApiIds,
}: {
  realmApiId: string;
  leagueName: string;
  baseCurrencyApiIds: string[];
}) {
  return queryOptions({
    queryKey: [
      "exchange",
      "snapshot-pairs",
      { realmApiId, leagueName, baseCurrencyApiIds },
    ],
    staleTime: SNAPSHOT_PAIRS_STALE_TIME_MS,
    queryFn: async () => {
      const payload = (await fetchRoute(
        `/api/${realmApiId}/Leagues/${leagueName}/SnapshotPairs`,
      )) as ExchangeSnapshotPairPayload[];
      const baseCurrencyApiIdSet = new Set(baseCurrencyApiIds);

      return payload.map((row) =>
        normalizeSnapshotPair(row, baseCurrencyApiIdSet),
      );
    },
  });
}
