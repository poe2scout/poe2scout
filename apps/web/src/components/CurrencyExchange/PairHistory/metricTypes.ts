export type DataKey = "currencyOneData" | "currencyTwoData";

export type MetricKey =
  | "pairPrice"
  | "valueTraded"
  | "volumeTraded"
  | "stockValue"
  | "highestStock";

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
