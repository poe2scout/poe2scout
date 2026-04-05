import { fetchNormalizedJson } from "../../api/client";
import type {
  CurrencyExchangeSnapshot,
  CurrencyItem,
  CurrencyPairData,
  PairHistoryData,
  PairHistoryEntry,
  PairHistoryResponse,
  SnapshotPair,
} from "../../types";
import { BaseCurrencies, BaseCurrencyList } from "../ReferenceCurrencySelector";

interface CurrencyPairDataPayload {
  valueTraded?: string | number;
  valuetraded?: string | number;
  relativePrice?: string | number;
  stockValue?: string | number;
  volumeTraded?: string | number;
  highestStock?: string | number;
}

interface SnapshotPairPayload {
  volume: string | number;
  currencyOne: CurrencyItem;
  currencyTwo: CurrencyItem;
  currencyOneData: CurrencyPairDataPayload;
  currencyTwoData: CurrencyPairDataPayload;
}

interface SnapshotHistoryPayload {
  data?: CurrencyExchangeSnapshot[];
  meta?: {
    hasMore?: boolean;
  };
}

interface PairHistoryDataPayload extends CurrencyPairDataPayload {
  currencyItemId: number;
}

interface PairHistoryEntryPayload {
  epoch: number;
  data: {
    currencyOneData: PairHistoryDataPayload;
    currencyTwoData: PairHistoryDataPayload;
  };
}

interface PairHistoryPayload {
  history?: PairHistoryEntryPayload[];
  meta?: {
    hasMore?: boolean;
  };
}

const toNumber = (value: string | number | null | undefined): number => {
  if (value === null || value === undefined) {
    return 0;
  }

  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const normalizeSnapshot = (
  snapshot: CurrencyExchangeSnapshot,
): CurrencyExchangeSnapshot => ({
  epoch: snapshot.epoch,
  volume: toNumber(snapshot.volume),
  marketCap: toNumber(snapshot.marketCap),
});

const normalizePairData = (
  data: CurrencyPairDataPayload,
): CurrencyPairData => {
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
};

const computePairPrices = (
  first: CurrencyPairData,
  second: CurrencyPairData,
): [CurrencyPairData, CurrencyPairData] => {
  const safeDivide = (numerator: number, denominator: number) =>
    denominator > 0 ? numerator / denominator : 0;

  const firstPairPrice = safeDivide(second.volumeTraded, first.volumeTraded);
  const secondPairPrice = safeDivide(first.volumeTraded, second.volumeTraded);

  return [
    { ...first, pairPrice: firstPairPrice },
    { ...second, pairPrice: secondPairPrice },
  ];
};

const isBaseCurrency = (item: CurrencyItem) =>
  BaseCurrencyList.includes(item.apiId as BaseCurrencies);

const normalizeSnapshotPair = (row: SnapshotPairPayload): SnapshotPair => {
  const currencyOneData = normalizePairData(row.currencyOneData);
  const currencyTwoData = normalizePairData(row.currencyTwoData);
  const areBothCurrencyBases =
    isBaseCurrency(row.currencyOne) && isBaseCurrency(row.currencyTwo);

  if (areBothCurrencyBases) {
    const isCorrectOrder =
      currencyOneData.volumeTraded <= currencyTwoData.volumeTraded;

    if (isCorrectOrder) {
      const [firstWithPrice, secondWithPrice] = computePairPrices(
        currencyOneData,
        currencyTwoData,
      );
      return {
        volume: toNumber(row.volume),
        currencyOne: row.currencyOne,
        currencyTwo: row.currencyTwo,
        currencyOneData: firstWithPrice,
        currencyTwoData: secondWithPrice,
      };
    }

    const [firstWithPrice, secondWithPrice] = computePairPrices(
      currencyTwoData,
      currencyOneData,
    );
    return {
      volume: toNumber(row.volume),
      currencyOne: row.currencyTwo,
      currencyTwo: row.currencyOne,
      currencyOneData: firstWithPrice,
      currencyTwoData: secondWithPrice,
    };
  }

  if (!isBaseCurrency(row.currencyOne)) {
    const [firstWithPrice, secondWithPrice] = computePairPrices(
      currencyOneData,
      currencyTwoData,
    );
    return {
      volume: toNumber(row.volume),
      currencyOne: row.currencyOne,
      currencyTwo: row.currencyTwo,
      currencyOneData: firstWithPrice,
      currencyTwoData: secondWithPrice,
    };
  }

  const [firstWithPrice, secondWithPrice] = computePairPrices(
    currencyTwoData,
    currencyOneData,
  );
  return {
    volume: toNumber(row.volume),
    currencyOne: row.currencyTwo,
    currencyTwo: row.currencyOne,
    currencyOneData: firstWithPrice,
    currencyTwoData: secondWithPrice,
  };
};

const normalizePairHistoryEntry = (
  entry: PairHistoryEntryPayload,
): PairHistoryEntry => {
  const normalizeData = (data: PairHistoryDataPayload): PairHistoryData => {
    const baseData = normalizePairData(data);

    return {
      currencyItemId: data.currencyItemId,
      ...baseData,
    };
  };

  const currencyOneData = normalizeData(entry.data.currencyOneData);
  const currencyTwoData = normalizeData(entry.data.currencyTwoData);
  const [currencyOneWithPrice, currencyTwoWithPrice] = computePairPrices(
    currencyOneData,
    currencyTwoData,
  );

  return {
    epoch: entry.epoch,
    data: {
      currencyOneData: currencyOneWithPrice as PairHistoryData,
      currencyTwoData: currencyTwoWithPrice as PairHistoryData,
    },
  };
};

export const fetchCurrentSnapshot = async (
  leagueName: string,
): Promise<CurrencyExchangeSnapshot> => {
  const payload = await fetchNormalizedJson<CurrencyExchangeSnapshot>(
    `/Leagues/${encodeURIComponent(leagueName)}/ExchangeSnapshot`,
  );

  return normalizeSnapshot(payload);
};

export const fetchSnapshotHistory = async (
  leagueName: string,
  limit: number,
  endEpoch?: number,
): Promise<{
  data: CurrencyExchangeSnapshot[];
  hasMore: boolean;
}> => {
  const payload = await fetchNormalizedJson<SnapshotHistoryPayload>(
    `/Leagues/${encodeURIComponent(leagueName)}/SnapshotHistory`,
    {
      Limit: limit,
      EndEpoch: endEpoch,
    },
  );

  return {
    data: (payload.data ?? []).map(normalizeSnapshot),
    hasMore: Boolean(payload.meta?.hasMore),
  };
};

export const fetchSnapshotPairs = async (
  leagueName: string,
): Promise<SnapshotPair[]> => {
  const rows = await fetchNormalizedJson<SnapshotPairPayload[]>(
    `/Leagues/${encodeURIComponent(leagueName)}/SnapshotPairs`,
  );

  return rows.map(normalizeSnapshotPair);
};

interface FetchPairHistoryParams {
  leagueName: string;
  currencyOneItemId: number;
  currencyTwoItemId: number;
  limit: number;
  endEpoch?: number;
}

export const fetchPairHistory = async ({
  leagueName,
  currencyOneItemId,
  currencyTwoItemId,
  limit,
  endEpoch,
}: FetchPairHistoryParams): Promise<PairHistoryResponse> => {
  const payload = await fetchNormalizedJson<PairHistoryPayload>(
    `/Leagues/${encodeURIComponent(leagueName)}/Currencies/Pairs/${currencyOneItemId}/${currencyTwoItemId}/History`,
    {
      Limit: limit,
      EndEpoch: endEpoch,
    },
  );

  return {
    history: (payload.history ?? []).map(normalizePairHistoryEntry),
    hasMore: Boolean(payload.meta?.hasMore),
  };
};
