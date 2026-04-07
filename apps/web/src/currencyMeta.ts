export interface CurrencyMetaSource {
  baseCurrencyApiId?: string;
  baseCurrencyText?: string;
  baseCurrencyIconUrl?: string | null;
  exaltedCurrencyText?: string;
  exaltedCurrencyIconUrl?: string | null;
  divineCurrencyText?: string;
  divineCurrencyIconUrl?: string | null;
  chaosCurrencyText?: string;
  chaosCurrencyIconUrl?: string | null;
}

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

const getCurrencyOverride = (
  apiId: string,
  source?: CurrencyMetaSource,
): { label?: string; iconUrl?: string | null } | null => {
  if (!source) {
    return null;
  }

  if (apiId === source.baseCurrencyApiId) {
    return {
      label: source.baseCurrencyText,
      iconUrl: source.baseCurrencyIconUrl,
    };
  }

  switch (apiId) {
    case "exalted":
      return {
        label: source.exaltedCurrencyText,
        iconUrl: source.exaltedCurrencyIconUrl,
      };
    case "divine":
      return {
        label: source.divineCurrencyText,
        iconUrl: source.divineCurrencyIconUrl,
      };
    case "chaos":
      return {
        label: source.chaosCurrencyText,
        iconUrl: source.chaosCurrencyIconUrl,
      };
    default:
      return null;
  }
};

export const getCurrencyLabel = (
  apiId: string,
  fallbackText?: string,
  source?: CurrencyMetaSource,
): string =>
  getCurrencyOverride(apiId, source)?.label ??
  CURRENCY_LABELS[apiId] ??
  fallbackText ??
  apiId;

export const getCurrencyIconUrl = (
  apiId: string,
  source?: CurrencyMetaSource,
): string | null =>
  getCurrencyOverride(apiId, source)?.iconUrl ?? CURRENCY_ICON_URLS[apiId] ?? null;
