import { Line } from "react-chartjs-2";
import { styled } from "@mui/material/styles";
import { PriceLogEntry } from "../../types";

interface PriceHistoryProps {
  priceHistory?: (PriceLogEntry | null)[];
  variant?: 'table' | 'compact';
}

const ChartContainer = styled("div")<{ variant?: 'table' | 'compact' }>(({ variant }) => ({
  display: "flex",
  alignItems: "center",
  gap: "16px",
  ...(variant === 'table' && {
    width: "160px",
    height: "40px",
  }),
  ...(variant === 'compact' && {
    width: "100%",
    minHeight: "40px",
    gap: "8px",
    justifyContent: "flex-end",
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

  let prices = [...priceHistory]
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

const chartOptions = {
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
      external: function (context: any) {
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
          const bodyLines = context.tooltip.body.map((b: any) => b.lines);

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
        label: (context: any) => {
          return `${context.parsed.y.toFixed(1)} ex`;
        },
        title: (tooltipItems: any) => {
          const index = tooltipItems[0].dataIndex;
          const hoursAgo = (6 - index) * 6;
          if (hoursAgo === 0) return "Now";
          if (hoursAgo === 6) return "6 hours ago";
          if (hoursAgo === 24) return "1 day ago";
          if (hoursAgo >= 24) {
            const days = Math.floor(hoursAgo / 24);
            const remainingHours = hoursAgo % 24;
            if (remainingHours === 0) {
              return `${days} ${days === 1 ? "day" : "days"} ago`;
            }
            return `${days}d ${remainingHours}h ago`;
          }
          return `${hoursAgo} hours ago`;
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
};

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

export function PriceHistory({ priceHistory, variant = 'compact' }: PriceHistoryProps) {
  if (!priceHistory) return null;

  const normalizedData = normalizeChartData(priceHistory);
  const priceChange = calculatePriceChange(priceHistory);

  const chartOptionsWithVariant = {
    ...chartOptions,
    maintainAspectRatio: true,
    aspectRatio: variant === 'table' ? 4 : 2.5,
    scales: {
      ...chartOptions.scales,
      x: {
        ...chartOptions.scales.x,
        grid: {
          display: false,
        },
      },
      y: {
        ...chartOptions.scales.y,
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
            "36h ago",
            "30h ago",
            "24h ago",
            "18h ago",
            "12h ago",
            "6h ago",
            "Now",
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
        options={chartOptionsWithVariant as any}
      />
      {renderPriceChange(priceChange)}
    </ChartContainer>
  );
}