export interface League {
  value: string;
  isCurrent: boolean;
  divinePrice: number;
  chaosDivinePrice: number;
  baseCurrencyApiId: string;
  baseCurrencyText: string;
  baseCurrencyIconUrl: string;
  exaltedCurrencyText: string;
  exaltedCurrencyIconUrl: string;
  divineCurrencyText: string;
  divineCurrencyIconUrl: string;
  chaosCurrencyText: string;
  chaosCurrencyIconUrl: string;
}

export interface Realm {
  value: string;
  label: string;
  gameApiId: string;
  realmApiId: string;
  tradeApiPath: string;
  defaultLeagueValue: string;
}
