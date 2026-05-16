import type {
  ExchangeCurrencyItem,
  ExchangePairHistoryData,
  ExchangePairHistoryEntry,
  ExchangePairData,
  ExchangeSnapshot,
  ExchangeSnapshotPair,
} from "../types";

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

export type ExchangePairHistoryDataPayload = ExchangePairDataPayload & {
  currencyItemId: number;
};

export type ExchangePairHistoryEntryPayload = {
  epoch: number;
  data: {
    currencyOneData: ExchangePairHistoryDataPayload;
    currencyTwoData: ExchangePairHistoryDataPayload;
  };
};

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

export function normalizePairData(
  data: ExchangePairDataPayload,
): ExchangePairData {
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

export function computePairPrices(
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

export function normalizePairHistoryEntry(
  entry: ExchangePairHistoryEntryPayload,
): ExchangePairHistoryEntry {
  const normalizeHistoryData = (
    data: ExchangePairHistoryDataPayload,
  ): ExchangePairHistoryData => ({
    currencyItemId: data.currencyItemId,
    ...normalizePairData(data),
  });

  const [currencyOneData, currencyTwoData] = computePairPrices(
    normalizeHistoryData(entry.data.currencyOneData),
    normalizeHistoryData(entry.data.currencyTwoData),
  ) as [ExchangePairHistoryData, ExchangePairHistoryData];

  return {
    epoch: entry.epoch,
    data: {
      currencyOneData,
      currencyTwoData,
    },
  };
}
