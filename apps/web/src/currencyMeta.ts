const CURRENCY_LABELS: Record<string, string> = {
  exalted: "Exalted Orb",
  divine: "Divine Orb",
  chaos: "Chaos Orb",
};

const CURRENCY_ICON_URLS: Record<string, string> = {
  exalted:
    "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lBZGRNb2RUb1JhcmUiLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/ad7c366789/CurrencyAddModToRare.png",
  chaos:
    "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lSZXJvbGxSYXJlIiwic2NhbGUiOjEsInJlYWxtIjoicG9lMiJ9XQ/c0ca392a78/CurrencyRerollRare.png",
  divine:
    "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lNb2RWYWx1ZXMiLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/2986e220b3/CurrencyModValues.png",
};

export const getCurrencyLabel = (
  apiId: string,
  fallbackText?: string,
): string => CURRENCY_LABELS[apiId] ?? fallbackText ?? apiId;

export const getCurrencyIconUrl = (apiId: string): string | null =>
  CURRENCY_ICON_URLS[apiId] ?? null;
