export type CategoryPriceHistoryConfig = {
  dataPoints: number;
  frequencyHours: number;
};

export const UNIQUE_PRICE_HISTORY_CONFIG: CategoryPriceHistoryConfig = {
  dataPoints: 7,
  frequencyHours: 24,
};

export const CURRENCY_PRICE_HISTORY_CONFIG: CategoryPriceHistoryConfig = {
  dataPoints: 8,
  frequencyHours: 6,
};

export function formatPriceHistoryLabel({
  dataPoints,
  frequencyHours,
}: CategoryPriceHistoryConfig) {
  const totalHours = dataPoints * frequencyHours;
  const rangeLabel =
    totalHours % 24 === 0
      ? `${totalHours / 24} ${totalHours === 24 ? "day" : "days"}`
      : `${totalHours} ${totalHours === 1 ? "hour" : "hours"}`;

  if (frequencyHours === 24) {
    return `${rangeLabel} history`;
  }

  return `${rangeLabel} history (${frequencyHours}h buckets)`;
}
