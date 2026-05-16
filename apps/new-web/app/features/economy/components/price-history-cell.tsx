import type { PriceLogEntry } from "../types";

const CHART_WIDTH = 120;
const CHART_HEIGHT = 36;
const CHART_PADDING = 3;

type PriceChange = {
  percentageChange: number;
  isPositive: boolean;
};

export default function PriceHistoryCell({
  priceLogs,
  referenceCurrencyLabel,
}: {
  priceLogs: (PriceLogEntry | null)[];
  referenceCurrencyLabel: string;
}) {
  const priceChange = calculatePriceChange(priceLogs);
  const chartData = normalizeChartData(priceLogs);

  if (!priceChange || !chartData) {
    return (
      <div className="flex h-9 w-46 items-center justify-end text-xs text-white/45">
        No data
      </div>
    );
  }

  const linePath = buildLinePath(chartData);
  const areaPath = buildAreaPath(chartData);
  const changeLabel = `${priceChange.isPositive ? "+" : ""}${priceChange.percentageChange.toFixed(1)}%`;
  const colorClass = priceChange.isPositive
    ? "text-emerald-400"
    : "text-red-400";
  const title = `7 day history: ${changeLabel} in ${referenceCurrencyLabel}`;

  return (
    <div
      className={`flex h-9 w-46 items-center justify-end gap-3 ${colorClass}`}
      title={title}
    >
      <svg
        aria-label={title}
        className="h-9 w-30 shrink-0"
        role="img"
        viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
      >
        <title>{title}</title>
        <path d={areaPath} fill="currentColor" opacity="0.12" />
        <path
          d={linePath}
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
        />
      </svg>
      <span className="w-13 text-right text-sm font-medium whitespace-nowrap">
        {changeLabel}
      </span>
    </div>
  );
}

function normalizeChartData(priceLogs: (PriceLogEntry | null)[]) {
  if (priceLogs.length === 0) {
    return null;
  }

  const prices = priceLogs
    .slice()
    .reverse()
    .map((entry) => getValidPrice(entry));
  const validPriceCount = prices.filter((price) => price != null).length;

  if (validPriceCount < 2) {
    return null;
  }

  const firstValidIndex = prices.findIndex((price) => price != null);
  const firstValidValue = prices[firstValidIndex];

  for (let index = 0; index < firstValidIndex; index += 1) {
    prices[index] = firstValidValue;
  }

  for (let index = 1; index < prices.length; index += 1) {
    if (prices[index] == null) {
      prices[index] = prices[index - 1];
    }
  }

  return prices.filter((price) => price != null);
}

function calculatePriceChange(
  priceLogs: (PriceLogEntry | null)[],
): PriceChange | null {
  const validPrices = priceLogs
    .map((entry) => getValidPrice(entry))
    .filter((price) => price != null);

  if (validPrices.length < 2) {
    return null;
  }

  const newestPrice = validPrices[0];
  const oldestPrice = validPrices[validPrices.length - 1];

  if (oldestPrice === 0) {
    return null;
  }

  const percentageChange = ((newestPrice - oldestPrice) / oldestPrice) * 100;

  return {
    percentageChange,
    isPositive: newestPrice >= oldestPrice,
  };
}

function buildLinePath(values: number[]) {
  const points = getChartPoints(values);

  if (points.length === 0) {
    return "";
  }

  if (points.length === 1) {
    return `M ${points[0].x} ${points[0].y}`;
  }

  return points.reduce((path, point, index) => {
    if (index === 0) {
      return `M ${point.x} ${point.y}`;
    }

    const previous = points[index - 1];
    const controlX = (previous.x + point.x) / 2;

    return `${path} C ${controlX} ${previous.y}, ${controlX} ${point.y}, ${point.x} ${point.y}`;
  }, "");
}

function buildAreaPath(values: number[]) {
  const points = getChartPoints(values);

  if (points.length === 0) {
    return "";
  }

  const linePath = buildLinePath(values);
  const baseline = CHART_HEIGHT - CHART_PADDING;
  const firstPoint = points[0];
  const lastPoint = points[points.length - 1];

  return `${linePath} L ${lastPoint.x} ${baseline} L ${firstPoint.x} ${baseline} Z`;
}

function getChartPoints(values: number[]) {
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const range = maxValue - minValue;
  const drawableWidth = CHART_WIDTH - CHART_PADDING * 2;
  const drawableHeight = CHART_HEIGHT - CHART_PADDING * 2;
  const xStep = values.length > 1 ? drawableWidth / (values.length - 1) : 0;

  return values.map((value, index) => {
    const normalizedY = range === 0 ? 0.5 : (value - minValue) / range;
    const x = round(CHART_PADDING + index * xStep);
    const y = round(CHART_PADDING + (1 - normalizedY) * drawableHeight);

    return { x, y };
  });
}

function getValidPrice(entry: PriceLogEntry | null) {
  if (entry == null || !Number.isFinite(entry.price) || entry.price === 0) {
    return null;
  }

  return entry.price;
}

function round(value: number) {
  return Math.round(value * 100) / 100;
}
