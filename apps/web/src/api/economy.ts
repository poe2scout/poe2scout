import { fetchNormalizedJson } from "./client";
import type {
  ApiItem,
  CategoryResponse,
  ItemHistoryResponse,
  PaginatedResponse,
  SearchableItem,
} from "../types";

interface LeaguePayload {
  value: string;
  divinePrice: number;
  chaosDivinePrice: number;
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

export const fetchLeagues = async (): Promise<LeaguePayload[]> => {
  const data = await fetchNormalizedJson<LeaguePayload[] | LeagueResponse>(
    "Leagues",
  );

  return Array.isArray(data) ? data : data.leagues ?? [];
};

export const fetchCategories = async (): Promise<CategoryResponse> =>
  fetchNormalizedJson<CategoryResponse>("/Items/Categories");

export const fetchSearchableItems = async (): Promise<SearchableItem[]> => {
  const data = await fetchNormalizedJson<
    SearchableItemsResponse | SearchableItem[]
  >(
    "Static/Filters",
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
  );

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

export const fetchLandingSplashItems = async (): Promise<ApiItem[]> => {
  const data = await fetchNormalizedJson<LandingSplashResponse>(
    "Static/LandingSplashInfo",
  );

  return data.items ?? [];
};
