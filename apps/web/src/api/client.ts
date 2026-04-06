type QueryValue = string | number | boolean | null | undefined;
type ApiScope = "realm" | "root";

const API_BASE_URL = import.meta.env.VITE_API_URL;
let activeRealmPath = "poe2";

const withTrailingSlash = (value: string): string =>
  value.endsWith("/") ? value : `${value}/`;

export const setActiveRealmPath = (realmPath: string): void => {
  activeRealmPath = realmPath;
};

export const getApiBaseUrl = (): string => API_BASE_URL;

const getScopedBaseUrl = (scope: ApiScope): string => {
  const normalizedBaseUrl = withTrailingSlash(API_BASE_URL);
  const url = new URL(normalizedBaseUrl);

  if (scope === "realm") {
    return url.toString();
  }

  const pathSegments = url.pathname.split("/").filter(Boolean);
  const apiSegmentIndex = pathSegments.lastIndexOf("api");

  if (apiSegmentIndex >= 0) {
    url.pathname = `/${pathSegments.slice(0, apiSegmentIndex + 1).join("/")}/`;
  }

  return url.toString();
};

const toCamelCase = (key: string): string => {
  const normalized = key
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1_$2")
    .replace(/([a-z0-9])([A-Z])/g, "$1_$2")
    .replace(/[-\s]+/g, "_")
    .toLowerCase();

  return normalized.replace(/_([a-z0-9])/g, (_, char: string) =>
    char.toUpperCase(),
  );
};

export const normalizeApiKeys = <T>(value: unknown): T => {
  if (Array.isArray(value)) {
    return value.map((entry) => normalizeApiKeys(entry)) as T;
  }

  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, entry]) => [
        toCamelCase(key),
        normalizeApiKeys(entry),
      ]),
    ) as T;
  }

  return value as T;
};

export const buildApiUrl = (
  path: string,
  query?: Record<string, QueryValue>,
  scope: ApiScope = "realm",
): string => {
  const normalizedPath = path.replace(/^\/+/, "");
  const scopedPath =
    scope === "realm"
      ? `${encodeURIComponent(activeRealmPath)}/${normalizedPath}`
      : normalizedPath;
  const url = new URL(scopedPath, getScopedBaseUrl(scope));

  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });

  return url.toString();
};

export const fetchNormalizedJson = async <T>(
  path: string,
  query?: Record<string, QueryValue>,
  scope: ApiScope = "realm",
): Promise<T> => {
  const response = await fetch(buildApiUrl(path, query, scope));

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return normalizeApiKeys<T>(data);
};
