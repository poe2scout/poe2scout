export type ExchangeSnapshot = {
  epoch: number;
  volume: number;
  marketCap: number;
  baseCurrencyApiId: string;
  baseCurrencyText: string;
};

export type ExchangeCurrencyMetadata = {
  name?: string;
  baseType?: string;
  stackSize?: number;
  maxStackSize?: number;
  description?: string;
  effect?: string[];
  flavorText?: string | null;
};

export type ExchangeCurrencyItem = {
  currencyItemId: number;
  itemId: number;
  currencyCategoryId: number;
  apiId: string;
  text: string;
  categoryApiId: string;
  iconUrl: string | null;
  itemMetadata: ExchangeCurrencyMetadata | null;
};

export type ExchangePairData = {
  valueTraded: number;
  relativePrice: number;
  stockValue: number;
  volumeTraded: number;
  highestStock: number;
  pairPrice: number;
};

export type ExchangeSnapshotPair = {
  currencyExchangeSnapshotPairId: number;
  currencyExchangeSnapshotId: number;
  volume: number;
  baseCurrencyApiId: string;
  baseCurrencyText: string;
  currencyOne: ExchangeCurrencyItem;
  currencyTwo: ExchangeCurrencyItem;
  currencyOneData: ExchangePairData;
  currencyTwoData: ExchangePairData;
};

export type ExchangePairHistoryData = ExchangePairData & {
  currencyItemId: number;
};

export type ExchangePairHistoryEntry = {
  epoch: number;
  data: {
    currencyOneData: ExchangePairHistoryData;
    currencyTwoData: ExchangePairHistoryData;
  };
};

export type ExchangePairHistoryResponse = {
  history: ExchangePairHistoryEntry[];
  hasMore: boolean;
  baseCurrencyApiId: string;
  baseCurrencyText: string;
};

export type SnapshotHistoryResponse = {
  data: ExchangeSnapshot[];
  hasMore: boolean;
  baseCurrencyApiId: string;
  baseCurrencyText: string;
};

export type ExchangeSort = "pair" | "volume";
export type ExchangeOrder = "asc" | "desc";

export type ExchangeTableState = {
  search: string;
  sort: ExchangeSort;
  order: ExchangeOrder;
  page: number;
  perPage: number;
};

export type ExchangePairHistoryDataKey = "currencyOneData" | "currencyTwoData";

export type ExchangePairHistoryMetricKey =
  | "pairPrice"
  | "valueTraded"
  | "volumeTraded"
  | "stockValue"
  | "highestStock";

export type ExchangePairHistoryMetricOption = {
  id: string;
  dataKey: ExchangePairHistoryDataKey;
  metricKey: ExchangePairHistoryMetricKey;
  label: string;
  itemName: string;
  counterpartName: string;
};
