export interface PriceLogEntry {
  price: number;
  time: string;
  quantity: number;
}

export interface CurrencyItem {
  id: number;
  itemId: number;
  currencyCategoryId: number;
  apiId: string;
  text: string;
  iconUrl: string | null;
  categoryApiId: string;
  itemMetadata: CurrencyMetadata | null;
}

export interface UniqueItemExtended {
  id: number;
  itemId: number;
  apiId: string;
  categoryApiId: string;
  iconUrl: string | null;
  text: string;
  name: string;
  type: string;
  itemMetadata: ItemMetadata | null;
  priceLogs: (PriceLogEntry | null)[];
  currentPrice: number | null;
  isChanceable: boolean;
}

export interface UniqueBaseItem {
  id: number;
  iconUrl: string | null;
  itemMetadata: ItemMetadata | null;
  itemId: number;
  name: string;
  apiId: string;
  categoryApiId: string;
  priceLogs: (PriceLogEntry | null)[];
  currentPrice: number | null;
  averageUniquePrice: number | null;
  isChanceable: boolean;
}

export interface CurrencyItemExtended {
  id: number;
  itemId: number;
  currencyCategoryId: number;
  apiId: string;
  categoryApiId: string;
  text: string;
  iconUrl: string | null;
  priceLogs: (PriceLogEntry | null)[];
  currentPrice: number | null;
  type: string;
  itemMetadata: CurrencyMetadata | null;
}

export type ApiItem = UniqueItemExtended | CurrencyItemExtended;

export interface PaginatedResponse<
  T extends UniqueItemExtended | CurrencyItemExtended
> {
  currentPage: number;
  pages: number;
  total: number;
  items: T[];
}

export interface BuildInfo {
  class: string;
  count: number;
}

export interface SearchableItem {
  displayName: string;
  category: string;
  identifier: string;
}

export const ClassMapping: Record<string, string> = {
  Sorceress1: "Stormweaver",
  Ranger1: "Deadeye",
  Monk2: "Invoker",
  Witch1: "Infernalist",
  Warrior1: "Titan",
  Mercenary3: "Gemling Legionnaire",
  Ranger3: "Pathfinder",
  Warrior2: "Warbringer",
  Witch2: "Blood Mage",
  Sorceress2: "Chronomancer",
  Mercenary2: "Witchhunter",
  Monk3: "Acolyte of Chayula",
};

export interface ItemMetadata {
  name?: string;
  baseType?: string;
  properties?: Record<string, string | null>;
  requirements?: Record<string, string>;
  implicitMods?: string[];
  explicitMods?: string[];
  flavorText?: string | null;
  description?: string;
}

export interface CurrencyMetadata {
  name: string;
  baseType: string;
  stackSize: number;
  maxStackSize: number;
  description?: string;
  effect?: string[];
  flavorText?: string | null;
}

export interface Category {
  id: number;
  apiId: string;
  label: string;
  icon: string;
}

export interface CategoryResponse {
  uniqueCategories: Category[];
  currencyCategories: Category[];
}

export interface ItemHistoryResponse {
  priceHistory: PriceLogEntry[];
  hasMore: boolean;
}

export interface CurrencyExchangeSnapshot {
  epoch: number;
  volume: number;
  marketCap: number;
}

export interface CurrencyPairData {
  valueTraded: number;
  relativePrice: number;
  stockValue: number;
  volumeTraded: number;
  highestStock: number;
  pairPrice: number;
}

export interface SnapshotPair {
  volume: number;
  currencyOne: CurrencyItem;
  currencyTwo: CurrencyItem;
  currencyOneData: CurrencyPairData;
  currencyTwoData: CurrencyPairData;
}

export interface PairHistoryData extends CurrencyPairData {
  currencyItemId: number;
}

export interface PairHistoryEntry {
  epoch: number;
  data: {
    currencyOneData: PairHistoryData;
    currencyTwoData: PairHistoryData;
  };
}

export interface PairHistoryResponse {
  history: PairHistoryEntry[];
  hasMore: boolean;
}
