import { MetricKey } from "./metricTypes";

export const formatMetricValue = (metric: MetricKey, value: number) => {
  switch (metric) {
    case "valueTraded":
    case "stockValue":
      return value.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      });
    case "volumeTraded":
    case "highestStock":
      return value.toLocaleString();
    case "pairPrice":
    default:
      return value.toLocaleString(undefined, {
        minimumFractionDigits: 3,
        maximumFractionDigits: 3,
      });
  }
};
