import { Line } from "react-chartjs-2";
import { styled } from "@mui/material/styles";
import type { ChartOptions, TooltipItem, TooltipModel } from "chart.js";

import { PriceLogEntry } from "../../types";

interface PriceHistoryProps {
  priceHistory?: (PriceLogEntry | null)[];
  variant?: 'table' | 'compact';
  referenceCurrencyLabel?: string;
}

const ChartContainer = styled("div")<{ variant?: 'table' | 'compact' }>(({ variant }) => ({
  display: "flex",
  alignItems: "center",
  gap: "16px",
  ...(variant === 'table' && {
    width: "150px",
    height: "40px",
  }),

}));

const PercentageChange = styled("span")<{ isPositive: boolean }>(
  ({ isPositive }) => ({
    fontSize: "1.1em",
    fontWeight: 500,
    color: isPositive ? "#4caf50" : "#f44336",
    whiteSpace: "nowrap",
  })
);

const normalizeChartData = (priceHistory: (PriceLogEntry | null)[]) => {
  if (!priceHistory || priceHistory.length === 0) return Array(7).fill(0);

  const prices = [...priceHistory]
    .reverse()
    .map((entry) => entry?.price || null);

  const firstValidIndex = prices.findIndex((price) => price !== null);
  if (firstValidIndex === -1) return Array(7).fill(0);

  const firstValidValue = prices[firstValidIndex];
  for (let i = 0; i < firstValidIndex; i++) {
    prices[i] = firstValidValue;
  }

  for (let i = 1; i < prices.length; i++) {
    if (prices[i] === null) {
      prices[i] = prices[i - 1];
    }
  }

  return prices;
};

const calculatePriceChange = (priceHistory: (PriceLogEntry | null)[]) => {
  if (!priceHistory || priceHistory.length < 2) return null;

  const validPrices = priceHistory.filter((p) => p && p.price !== null);
  if (validPrices.length < 2) return null;

  const firstPrice = validPrices[validPrices.length - 1]?.price;
  const lastPrice = validPrices[0]?.price;
  if (!firstPrice || !lastPrice) return null;
  const percentageChange = ((lastPrice - firstPrice) / firstPrice) * 100;

  return {
    percentageChange,
    isPositive: lastPrice >= firstPrice,
  };
};

interface ExternalTooltipContext {
  chart: {
    canvas: HTMLCanvasElement;
  };
  tooltip: TooltipModel<"line">;
}

const buildChartOptions = (
  referenceCurrencyLabel: string,
): ChartOptions<"line"> => ({
  layout: {
    padding: {
      top: 1,
      bottom: 1,
    },
  },
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 4,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: false,
      mode: "index",
      intersect: false,
      position: "nearest",
      external: (context: ExternalTooltipContext) => {
        // Get tooltip element
        const tooltipEl = document.getElementById("chartjs-tooltip");

        // Create tooltip if it doesn't exist
        if (!tooltipEl) {
          const div = document.createElement("div");
          div.id = "chartjs-tooltip";
          div.style.position = "fixed";
          div.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
          div.style.padding = "8px";
          div.style.borderRadius = "4px";
          div.style.zIndex = "1000";
          div.style.pointerEvents = "none";
          document.body.appendChild(div);
        }

        // Hide if no tooltip
        if (context.tooltip.opacity === 0) {
          tooltipEl!.style.display = "none";
          return;
        }

        // Set Text
        if (context.tooltip.body) {
          const titleLines = context.tooltip.title || [];
          const bodyLines = context.tooltip.body.map((body) => body.lines);

          let innerHtml = "<div>";
          titleLines.forEach((title: string) => {
            innerHtml += `<div style="font-size: 12px; color: #fff">${title}</div>`;
          });
          bodyLines.forEach((body: string[]) => {
            innerHtml += `<div style="font-size: 12px; color: #fff">${body}</div>`;
          });
          innerHtml += "</div>";

          tooltipEl!.innerHTML = innerHtml;
        }

        // Position tooltip
        const position = context.chart.canvas.getBoundingClientRect();
        tooltipEl!.style.display = "block";
        tooltipEl!.style.left = position.left + context.tooltip.caretX + "px";
        tooltipEl!.style.top =
          position.top +
          context.tooltip.caretY -
          tooltipEl!.offsetHeight -
          8 +
          "px";
      },
      callbacks: {
        label: (context: TooltipItem<"line">) => {
          return `${context.parsed.y.toFixed(1)} ${referenceCurrencyLabel}`;
        },
        title: (tooltipItems: TooltipItem<"line">[]) => {
          const index = tooltipItems[0].dataIndex;
          const daysAgo = 6 - index;
          if (daysAgo === 0) return "Today";
          if (daysAgo === 1) return "Yesterday";
          return `${daysAgo} days ago`;
        },
      },
    },
  },
  scales: {
    x: {
      display: false,
    },
    y: {
      display: false,
    },
  },
  interaction: {
    intersect: false,
    mode: "index",
  },
});

const renderPriceChange = (
  priceChange: { percentageChange: number; isPositive: boolean } | null
) => {
  if (!priceChange) return <span>No data</span>;

  return (
    <PercentageChange isPositive={priceChange.isPositive}>
      {priceChange.isPositive ? "+" : ""}
      {priceChange.percentageChange.toFixed(1)}%
    </PercentageChange>
  );
};

export function PriceHistory({
  priceHistory,
  variant = 'compact',
  referenceCurrencyLabel = "base",
}: PriceHistoryProps) {
  if (!priceHistory) return null;

  const normalizedData = normalizeChartData(priceHistory);
  const priceChange = calculatePriceChange(priceHistory);
  const chartOptions = buildChartOptions(referenceCurrencyLabel);
  const chartScales = chartOptions.scales ?? {};

  const chartOptionsWithVariant = {
    ...chartOptions,
    maintainAspectRatio: true,
    aspectRatio: variant === 'table' ? 4 : 2.5,
    scales: {
      ...chartScales,
      x: {
        ...chartScales.x,
        grid: {
          display: false,
        },
      },
      y: {
        ...chartScales.y,
        grid: {
          display: false,
        },
      },
    },
  };

  return (
    <ChartContainer variant={variant}>
      <Line
        data={{
          labels: [
            "6 days ago",
            "5 days ago",
            "4 days ago",
            "3 days ago",
            "2 days ago",
            "Yesterday",
            "Today",
          ],
          datasets: [
            {
              data: normalizedData,
              borderColor: priceChange?.isPositive ? "#4caf50" : "#f44336",
              backgroundColor: priceChange?.isPositive
                ? "rgba(76, 175, 80, 0.1)"
                : "rgba(244, 67, 54, 0.1)",
              tension: 0.4,
              fill: true,
              pointRadius: 0,
              borderWidth: 2,
              pointHoverRadius: 4,
              pointHoverBackgroundColor: priceChange?.isPositive
                ? "#4caf50"
                : "#f44336",
              pointHoverBorderColor: "#fff",
              pointHoverBorderWidth: 2,
            },
          ],
        }}
        options={chartOptionsWithVariant}
      />
      {renderPriceChange(priceChange)}
    </ChartContainer>
  );
}
