export type DataKey = "CurrencyOneData" | "CurrencyTwoData";

export type MetricKey =
  | "PairPrice"
  | "ValueTraded"
  | "VolumeTraded"
  | "StockValue"
  | "HighestStock";

export interface MetricOption {
  id: string;
  dataKey: DataKey;
  metricKey: MetricKey;
  menuLabel: string;
  itemName: string;
  counterpartName: string;
}

export interface MetricMenuOption {
  id: string;
  menuLabel: string;
}
