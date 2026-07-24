export type PriceLogEntry = {
  price: number;
  time: string;
  quantity: number;
};

export type ItemMetadata = {
  name?: string;
  baseType?: string;
  properties?: Record<string, string | null>;
  requirements?: Record<string, string>;
  implicitMods?: string[];
  explicitMods?: string[];
  flavorText?: string | null;
  description?: string;
};

export type CurrencyMetadata = {
  name?: string;
  baseType?: string;
  stackSize?: number;
  maxStackSize?: number;
  description?: string;
  effect?: string[];
  flavorText?: string | null;
};

type EconomyItemBase = {
  itemId: number;
  categoryApiId: string;
  iconUrl: string | null;
  itemMetadata: ItemMetadata | CurrencyMetadata | null;
  priceLogs: (PriceLogEntry | null)[];
  currentPrice: number | null;
  currentQuantity: number | null;
};

export type CurrencyEconomyItem = EconomyItemBase & {
  currencyItemId: number;
  currencyCategoryId: number;
  apiId: string | null;
  baseItemTypeId: string | null;
  text: string;
};

export type UniqueEconomyItem = EconomyItemBase & {
  uniqueItemId: number;
  text: string;
  name: string;
  type: string;
  isChanceable: boolean | null;
};

export type EconomyItem = CurrencyEconomyItem | UniqueEconomyItem;

export type PaginatedEconomyResponse<T extends EconomyItem> = {
  currentPage: number;
  pages: number;
  total: number;
  items: T[];
};

export type ItemSummary = {
  itemId: number;
  categoryApiId: string;
  text: string;
  name: string | null;
  type: string | null;
  apiId: string | null;
  baseItemTypeId: string | null;
  currentPrice: number | null;
  iconUrl: string | null;
};

export type ItemHistoryResponse = {
  priceHistory: PriceLogEntry[];
  hasMore: boolean;
};

export type DailyStatEntry = {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  average: number;
  volume: number;
};

export type ItemDailyStatsHistoryResponse = {
  dailyStats: DailyStatEntry[];
  hasMore: boolean;
  baseCurrencyApiId: string | null;
  baseCurrencyBaseItemTypeId: string | null;
  baseCurrencyText: string;
};
