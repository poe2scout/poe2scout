type QueryValue = string | number | boolean | null | undefined;

const API_BASE_URL = import.meta.env.VITE_API_URL;

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
): string => {
  const url = new URL(path, API_BASE_URL);

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
): Promise<T> => {
  const response = await fetch(buildApiUrl(path, query));

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return normalizeApiKeys<T>(data);
};
