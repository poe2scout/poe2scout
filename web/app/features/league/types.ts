export interface LeagueCurrency {
  apiId: string;
  text: string;
  iconUrl: string | null;
  relativePrice: number;
}

export interface League {
  value: string;
  shortName: string;
  isCurrent: boolean;
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
  defaultCurrency: LeagueCurrency;
}

export interface Realm {
  value: string;
  label: string;
  gameApiId: string;
  realmApiId: string;
  tradeApiPath: string;
  defaultLeagueValue: string;
}
