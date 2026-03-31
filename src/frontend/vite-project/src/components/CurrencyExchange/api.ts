import { League } from "../../contexts/LeagueContext";
import { CurrencyItem } from "../../types";
import { BaseCurrencies, BaseCurrencyList } from "../ReferenceCurrencySelector";

export const CURRENCY_EXCHANGE_API_URL = import.meta.env.VITE_API_URL;

export interface CurrencyPairDataDto {
  ValueTraded: string;
  RelativePrice: string;
  StockValue: string;
  VolumeTraded: number;
  HighestStock: number;
}

export interface SnapshotPairDto {
  Volume: string;
  CurrencyOne: CurrencyItem;
  CurrencyTwo: CurrencyItem;
  CurrencyOneData: CurrencyPairDataDto;
  CurrencyTwoData: CurrencyPairDataDto;
}

export interface CurrencyPairData {
  ValueTraded: number;
  RelativePrice: number;
  StockValue: number;
  VolumeTraded: number;
  HighestStock: number;
  PairPrice: number;
}

export interface SnapshotPair {
  Volume: number;
  CurrencyOne: CurrencyItem;
  CurrencyTwo: CurrencyItem;
  CurrencyOneData: CurrencyPairData;
  CurrencyTwoData: CurrencyPairData;
}

const toNumber = (value: string | number | null | undefined): number => {
  if (value === null || value === undefined) {
    return 0;
  }

  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const normalizePairData = (data: CurrencyPairDataDto): CurrencyPairData => {
  const volumeTraded = toNumber(data.VolumeTraded);
  const relativePrice = toNumber(data.RelativePrice);
  const explicitValue = toNumber(
    (data as unknown as { Valuetraded?: string }).Valuetraded ?? data.ValueTraded,
  );
  const derivedValue = relativePrice * volumeTraded;

  return {
    ValueTraded: derivedValue > 0 ? derivedValue : explicitValue,
    RelativePrice: relativePrice,
    StockValue: toNumber(data.StockValue),
    VolumeTraded: volumeTraded,
    HighestStock: toNumber(data.HighestStock),
    PairPrice: 0,
  };
};

const computePairPrices = (
  first: CurrencyPairData,
  second: CurrencyPairData,
): [CurrencyPairData, CurrencyPairData] => {
  const safeDivide = (numerator: number, denominator: number) =>
    denominator > 0 ? numerator / denominator : 0;

  const firstPairPrice = safeDivide(second.VolumeTraded, first.VolumeTraded);
  const secondPairPrice = safeDivide(first.VolumeTraded, second.VolumeTraded);

  return [
    { ...first, PairPrice: firstPairPrice },
    { ...second, PairPrice: secondPairPrice },
  ];
};

const normalizeSnapshotPair = (row: SnapshotPairDto): SnapshotPair => {
  const currencyOneData = normalizePairData(row.CurrencyOneData);
  const currencyTwoData = normalizePairData(row.CurrencyTwoData);

  const isCurrencyOneBase = BaseCurrencyList.includes(row.CurrencyOne.apiId as BaseCurrencies);
  const areBothCurrencyBases =
    BaseCurrencyList.includes(row.CurrencyOne.apiId as BaseCurrencies) &&
    BaseCurrencyList.includes(row.CurrencyTwo.apiId as BaseCurrencies);

  if (areBothCurrencyBases) {
    const isCorrectOrder = currencyOneData.VolumeTraded <= currencyTwoData.VolumeTraded;

    if (isCorrectOrder) {
      const [firstWithPrice, secondWithPrice] = computePairPrices(
        currencyOneData,
        currencyTwoData,
      );
      return {
        Volume: toNumber(row.Volume),
        CurrencyOne: row.CurrencyOne,
        CurrencyTwo: row.CurrencyTwo,
        CurrencyOneData: firstWithPrice,
        CurrencyTwoData: secondWithPrice,
      };
    }

    const [firstWithPrice, secondWithPrice] = computePairPrices(
      currencyTwoData,
      currencyOneData,
    );
    return {
      Volume: toNumber(row.Volume),
      CurrencyOne: row.CurrencyTwo,
      CurrencyTwo: row.CurrencyOne,
      CurrencyOneData: firstWithPrice,
      CurrencyTwoData: secondWithPrice,
    };
  }

  if (!isCurrencyOneBase) {
    const [firstWithPrice, secondWithPrice] = computePairPrices(
      currencyOneData,
      currencyTwoData,
    );
    return {
      Volume: toNumber(row.Volume),
      CurrencyOne: row.CurrencyOne,
      CurrencyTwo: row.CurrencyTwo,
      CurrencyOneData: firstWithPrice,
      CurrencyTwoData: secondWithPrice,
    };
  }

  const [firstWithPrice, secondWithPrice] = computePairPrices(
    currencyTwoData,
    currencyOneData,
  );
  return {
    Volume: toNumber(row.Volume),
    CurrencyOne: row.CurrencyTwo,
    CurrencyTwo: row.CurrencyOne,
    CurrencyOneData: firstWithPrice,
    CurrencyTwoData: secondWithPrice,
  };
};

export const fetchSnapshotPairs = async (league: League): Promise<SnapshotPair[]> => {
  const response = await fetch(`${CURRENCY_EXCHANGE_API_URL}/currencyExchange/SnapshotPairs?league=${league.value}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch snapshot pairs: ${response.statusText}`);
  }

  const rows: SnapshotPairDto[] = await response.json();
  return rows.map(normalizeSnapshotPair);
};

export interface PairHistoryDataDto {
  CurrencyItemId: number;
  ValueTraded?: string;
  Valuetraded?: string;
  RelativePrice: string;
  StockValue: string;
  VolumeTraded: number;
  HighestStock: number;
}

export interface PairHistoryEntryDto {
  Epoch: number;
  Data: {
    CurrencyOneData: PairHistoryDataDto;
    CurrencyTwoData: PairHistoryDataDto;
  };
}

export interface PairHistoryDto {
  History: PairHistoryEntryDto[];
  Meta?: {
    hasMore?: boolean;
  };
}

export interface PairHistoryData {
  CurrencyItemId: number;
  ValueTraded: number;
  RelativePrice: number;
  StockValue: number;
  VolumeTraded: number;
  HighestStock: number;
  PairPrice: number;
}

export interface PairHistoryEntry {
  Epoch: number;
  Data: {
    CurrencyOneData: PairHistoryData;
    CurrencyTwoData: PairHistoryData;
  };
}

export const normalizePairHistoryEntry = (entry: PairHistoryEntryDto): PairHistoryEntry => {
  const normalizeData = (data: PairHistoryDataDto): PairHistoryData => {
    const volumeTraded = toNumber(data.VolumeTraded);
    const relativePrice = toNumber(data.RelativePrice);
    const explicitValue = toNumber(data.ValueTraded ?? data.Valuetraded);
    const derivedValue = relativePrice * volumeTraded;
    const valueTraded = derivedValue > 0 ? derivedValue : explicitValue;

    return {
      CurrencyItemId: data.CurrencyItemId,
      ValueTraded: valueTraded,
      RelativePrice: relativePrice,
      StockValue: toNumber(data.StockValue),
      VolumeTraded: volumeTraded,
      HighestStock: toNumber(data.HighestStock),
      PairPrice: 0,
    };
  };

  const currencyOneData = normalizeData(entry.Data.CurrencyOneData);
  const currencyTwoData = normalizeData(entry.Data.CurrencyTwoData);
  const [currencyOneWithPrice, currencyTwoWithPrice] = computePairPrices(
    currencyOneData,
    currencyTwoData,
  );

  return {
    Epoch: entry.Epoch,
    Data: {
      CurrencyOneData: currencyOneWithPrice,
      CurrencyTwoData: currencyTwoWithPrice,
    },
  };
};

export const normalizePairHistoryResponse = (dto: PairHistoryDto) => {
  const history = (dto.History ?? []).map(normalizePairHistoryEntry);
  const hasMore = Boolean(dto.Meta?.hasMore);

  return { history, hasMore };
};

interface FetchPairHistoryParams {
  league: string;
  currencyOneItemId: number;
  currencyTwoItemId: number;
  limit: number;
  endEpoch?: number;
}

export const fetchPairHistory = async ({
  league,
  currencyOneItemId,
  currencyTwoItemId,
  limit,
  endEpoch,
}: FetchPairHistoryParams): Promise<PairHistoryDto> => {
  const url = new URL(`${CURRENCY_EXCHANGE_API_URL}/currencyExchange/PairHistory`);
  url.searchParams.set("league", league);
  url.searchParams.set("currencyOneItemId", currencyOneItemId.toString());
  url.searchParams.set("currencyTwoItemId", currencyTwoItemId.toString());
  url.searchParams.set("limit", limit.toString());

  if (endEpoch !== undefined) {
    url.searchParams.set("endEpoch", endEpoch.toString());
  }

  const response = await fetch(url.toString());

  if (!response.ok) {
    throw new Error(`Failed to fetch pair history: ${response.statusText}`);
  }

  return response.json();
};
