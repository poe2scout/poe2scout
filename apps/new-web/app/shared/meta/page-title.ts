import type { League, Realm } from "~/features/league/types";

export const SITE_NAME = "POE2 Scout";

type RouteMetaMatch = {
  id: string;
  data: unknown;
};

type RouteMetaMatches = ReadonlyArray<RouteMetaMatch | undefined>;

type LeagueRouteData = {
  league: League;
  realm: Realm;
};

type CategorySummary = {
  apiId: string;
  label: string;
};

type CategoryRouteData = {
  currencyCategories: CategorySummary[];
  uniqueCategories: CategorySummary[];
};

type ItemTitleSource = {
  itemId?: number;
  text?: string | null;
  name?: string | null;
  type?: string | null;
  itemMetadata?: {
    name?: string | null;
    baseType?: string | null;
  } | null;
};

export function formatTitle(parts: Array<string | null | undefined>) {
  const titleParts = parts
    .map((part) => part?.trim())
    .filter((part): part is string => Boolean(part));

  if (titleParts.length === 0) {
    return SITE_NAME;
  }

  return `${titleParts.join(" - ")} | ${SITE_NAME}`;
}

export function getLeagueContextTitle(matches: RouteMetaMatches) {
  const data = getLeagueRouteData(matches);

  if (!data) {
    return null;
  }

  return `${data.league.value} ${data.realm.realmApiId}`.trim();
}

export function getCategoryLabel(
  matches: RouteMetaMatches,
  kind: "currencies" | "uniques",
  categoryApiId: string | undefined,
) {
  if (!categoryApiId) {
    return kind === "currencies" ? "Currency" : "Unique";
  }

  const data = getCategoryRouteData(matches);
  const categories =
    kind === "currencies" ? data?.currencyCategories : data?.uniqueCategories;
  const category = categories?.find((entry) => entry.apiId === categoryApiId);

  return category?.label ?? formatCategoryFallback(categoryApiId);
}

export function getItemTitle(item: ItemTitleSource | null | undefined) {
  if (!item) {
    return "Item";
  }

  return (
    item.name ??
    item.text ??
    item.itemMetadata?.name ??
    item.itemMetadata?.baseType ??
    item.type ??
    (item.itemId ? `Item ${item.itemId}` : "Item")
  );
}

export function getPairTitleFallback(
  currencyOneItemId: string | undefined,
  currencyTwoItemId: string | undefined,
) {
  return `Pair ${currencyOneItemId ?? "?"} / ${currencyTwoItemId ?? "?"}`;
}

function getLeagueRouteData(matches: RouteMetaMatches) {
  const match = matches.find((entry) =>
    entry?.id.endsWith("/features/league/routes/layout"),
  );

  return isLeagueRouteData(match?.data) ? match.data : null;
}

function getCategoryRouteData(matches: RouteMetaMatches) {
  const match = matches.find((entry) =>
    entry?.id.endsWith("/features/economy/routes/layout"),
  );

  return isCategoryRouteData(match?.data) ? match.data : null;
}

function isLeagueRouteData(value: unknown): value is LeagueRouteData {
  if (!isRecord(value) || !isRecord(value.league) || !isRecord(value.realm)) {
    return false;
  }

  return typeof value.league.value === "string" &&
    typeof value.realm.realmApiId === "string";
}

function isCategoryRouteData(value: unknown): value is CategoryRouteData {
  if (!isRecord(value)) {
    return false;
  }

  return (
    Array.isArray(value.currencyCategories) &&
    Array.isArray(value.uniqueCategories)
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function formatCategoryFallback(value: string) {
  return value
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}
