import { MetricKey } from "./metricTypes";

export const formatMetricValue = (metric: MetricKey, value: number) => {
  switch (metric) {
    case "ValueTraded":
    case "StockValue":
      return value.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      });
    case "VolumeTraded":
    case "HighestStock":
      return value.toLocaleString();
    case "PairPrice":
    default:
      return value.toLocaleString(undefined, {
        minimumFractionDigits: 3,
        maximumFractionDigits: 3,
      });
  }
};
