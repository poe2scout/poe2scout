export interface PriceLogEntry {
  price: number;
  time: string;
  quantity: number;
}

export interface UniqueItemExtended {
  id: number;
  itemId: number;
  iconUrl: string | null;
  text: string;
  name: string;
  type: string;
  itemMetadata: ItemMetadata| null;
  priceLogs: (PriceLogEntry | null)[];
  currentPrice: number | null;
}

export interface UniqueBaseItem {
  id: number;
  iconUrl: string | null;
  itemMetadata: ItemMetadata| null
  itemId: number;
  name: string;
  apiId: string;
  priceLogs: (PriceLogEntry | null)[];
  currentPrice: number | null;
  averageUniquePrice: number | null;
}

export interface CurrencyItemExtended {
  id: number;
  itemId: number;
  currencyCategoryId: number;
  apiId: string;
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
  base_type?: string;
  properties: Record<string, string | null>;
  requirements: Record<string, string>;
  implicit_mods: string[];
  explicit_mods: string[];
  flavor_text?: string | null;
  description?: string;
}

export interface CurrencyMetadata {
  name: string;
  base_type: string;
  stack_size: number;
  max_stack_size: number;
  description?: string;
  effect?: string[];
  flavor_text?: string | null;
}

export interface Category {
  id: number;
  apiId: string;
  label: string;
  icon: string;
}

export interface CategoryResponse {
  unique_categories: Category[];
  currency_categories: Category[];
}
