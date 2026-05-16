import type { ExchangePairHistoryMetricKey } from "../types";

export const PAIR_HISTORY_METRIC_LABELS: Record<
  ExchangePairHistoryMetricKey,
  string
> = {
  pairPrice: "Price",
  valueTraded: "Value traded",
  volumeTraded: "Volume traded",
  stockValue: "Stock value",
  highestStock: "Stock",
};

export function formatPairHistoryMetric(
  metric: ExchangePairHistoryMetricKey,
  value: number,
) {
  switch (metric) {
    case "pairPrice":
      return value.toLocaleString(undefined, {
        minimumFractionDigits: 3,
        maximumFractionDigits: 3,
      });
    case "valueTraded":
    case "stockValue":
      return value.toLocaleString(undefined, {
        maximumFractionDigits: 0,
      });
    case "volumeTraded":
    case "highestStock":
    default:
      return value.toLocaleString();
  }
}
