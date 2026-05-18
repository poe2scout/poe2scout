import { fetchNormalizedJson, getActiveRealmPath } from "./client";
import type {
  ApiItem,
  CategoryResponse,
  ItemDailyStatsHistoryResponse,
  ItemHistoryResponse,
  PaginatedResponse,
  RealmOption,
  SearchableItem,
} from "../types";

interface LeaguePayload {
  value: string;
  divinePrice: number;
  chaosDivinePrice: number;
  baseCurrencyApiId: string;
  baseCurrencyText: string;
  baseCurrencyIconUrl: string | null;
  exaltedCurrencyText: string;
  exaltedCurrencyIconUrl: string | null;
  divineCurrencyText: string;
  divineCurrencyIconUrl: string | null;
  chaosCurrencyText: string;
  chaosCurrencyIconUrl: string | null;
}

interface LeagueResponse {
  leagues?: LeaguePayload[];
}

interface SearchableItemsResponse {
  filters?: SearchableItem[];
}

interface LandingSplashResponse {
  items: ApiItem[];
}

interface FetchItemsParams {
  category: string;
  page: number;
  perPage: number;
  leagueName: string;
  referenceCurrency: string;
  search?: string;
  isCurrencyCategory: boolean;
}

interface FetchItemHistoryParams {
  itemId: number;
  leagueName: string;
  logCount: number;
  referenceCurrency: string;
  endTime: string;
}

interface FetchItemDailyStatsHistoryParams {
  itemId: number;
  leagueName: string;
  dayCount: number;
  endDate?: string;
}

const getApiItemId = (item: ApiItem): number => {
  const itemWithNewIds = item as ApiItem & {
    uniqueItemId?: number;
    currencyItemId?: number;
  };

  return itemWithNewIds.uniqueItemId ?? itemWithNewIds.currencyItemId ?? item.id;
};

const withLegacyItemId = <T extends ApiItem>(item: T): T => ({
  ...item,
  id: getApiItemId(item),
});

export const fetchLeagues = async (): Promise<LeaguePayload[]> => {
  const data = await fetchNormalizedJson<LeaguePayload[] | LeagueResponse>(
    "Leagues",
  );

  return Array.isArray(data) ? data : data.leagues ?? [];
};

export const fetchRealmOptions = async (): Promise<RealmOption[]> =>
  fetchNormalizedJson<RealmOption[]>("Realms", undefined, "root");

export const fetchCategories = async (
  leagueName: string,
): Promise<CategoryResponse> =>
  fetchNormalizedJson<CategoryResponse>(
    `Leagues/${encodeURIComponent(leagueName)}/Items/Categories`,
  );

export const fetchSearchableItems = async (): Promise<SearchableItem[]> => {
  const data = await fetchNormalizedJson<
    SearchableItemsResponse | SearchableItem[]
  >(
    `Realms/${encodeURIComponent(getActiveRealmPath())}/Filters`,
    undefined,
    "root",
  );

  return Array.isArray(data) ? data : data.filters ?? [];
};

export const fetchItemsByCategory = async ({
  category,
  page,
  perPage,
  leagueName,
  referenceCurrency,
  search,
  isCurrencyCategory,
}: FetchItemsParams): Promise<PaginatedResponse<ApiItem>> =>
  fetchNormalizedJson<PaginatedResponse<ApiItem>>(
    `Leagues/${encodeURIComponent(leagueName)}/${isCurrencyCategory ? "Currencies" : "Uniques"}/ByCategory`,
    {
      Category: category,
      Page: page,
      PerPage: perPage,
      Search: search ?? "",
      ReferenceCurrency: referenceCurrency,
    },
  ).then((data) => ({
    ...data,
    items: data.items.map(withLegacyItemId),
  }));

export const fetchItemHistory = async ({
  itemId,
  leagueName,
  logCount,
  referenceCurrency,
  endTime,
}: FetchItemHistoryParams): Promise<ItemHistoryResponse> =>
  fetchNormalizedJson<ItemHistoryResponse>(`Leagues/${encodeURIComponent(leagueName)}/Items/${itemId}/History`, {
    LogCount: logCount,
    ReferenceCurrency: referenceCurrency,
    EndTime: endTime,
  });

export const fetchItemDailyStatsHistory = async ({
  itemId,
  leagueName,
  dayCount,
  endDate,
}: FetchItemDailyStatsHistoryParams): Promise<ItemDailyStatsHistoryResponse> =>
  fetchNormalizedJson<ItemDailyStatsHistoryResponse>(
    `Leagues/${encodeURIComponent(leagueName)}/Items/${itemId}/DailyStatsHistory`,
    {
      DayCount: dayCount,
      EndDate: endDate,
    },
  );

export const fetchLandingSplashItems = async (): Promise<ApiItem[]> => {
  const data = await fetchNormalizedJson<LandingSplashResponse>(
    `Realms/${encodeURIComponent(getActiveRealmPath())}/LandingSplashInfo`,
    undefined,
    "root",
  );

  return (data.items ?? []).map(withLegacyItemId);
};
