import type { League, LeagueCurrency } from "./types";

export type CurrencyIdentifiers = {
  apiId: string | null;
  baseItemTypeId: string | null;
};

export function getCurrencyIdentifier(currency: CurrencyIdentifiers): string {
  const identifier = currency.apiId ?? currency.baseItemTypeId;
  if (!identifier) {
    throw new Error("Currency has no identifier.");
  }

  return identifier;
}

export function getLeagueBaseCurrencyIdentifier(league: League): string {
  const identifier =
    league.baseCurrencyApiId ?? league.baseCurrencyBaseItemTypeId;
  if (!identifier) {
    throw new Error(`League ${league.value} base currency has no identifier.`);
  }

  return identifier;
}

export function getLeagueCurrencyIdentifier(currency: LeagueCurrency): string {
  return getCurrencyIdentifier(currency);
}
