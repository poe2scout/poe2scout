import {
  ColorType,
  HistogramSeries,
  LineSeries,
  createChart,
  type HistogramData,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type MouseEventParams,
  type Time,
  type UTCTimestamp,
} from "lightweight-charts";
import { useEffect, useMemo, useRef, useState } from "react";
import formatNumber from "~/shared/utils/format-number";
import type { ExchangeSnapshot } from "../types";
import formatEpoch from "../utils/format-epoch";

type LegendValues = {
  marketCap?: number;
  volume?: number;
  time?: UTCTimestamp;
};

export default function MarketHistoryChart({
  history,
  baseCurrencyText,
  hasMore,
  isLoading,
  isError,
  isLoadingMore,
  onLoadMore,
}: {
  history: ExchangeSnapshot[];
  baseCurrencyText: string;
  hasMore: boolean;
  isLoading: boolean;
  isError: boolean;
  isLoadingMore: boolean;
  onLoadMore: () => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const lineRef = useRef<ISeriesApi<"Line"> | null>(null);
  const histogramRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const loadingRef = useRef(false);
  const hasMoreRef = useRef(hasMore);
  const latestLegendRef = useRef<LegendValues>({});
  const onLoadMoreRef = useRef(onLoadMore);
  const justLoadedRef = useRef(false);
  const didFitContentRef = useRef(false);
  const [legend, setLegend] = useState<LegendValues>({});

  const chartData = useMemo(() => {
    const ordered = [...history].sort((a, b) => a.epoch - b.epoch);
    const lineData: LineData<Time>[] = ordered.map((entry) => ({
      time: entry.epoch as UTCTimestamp,
      value: entry.marketCap,
    }));
    const histogramData: HistogramData<Time>[] = ordered.map((entry) => ({
      time: entry.epoch as UTCTimestamp,
      value: entry.volume,
      color: "rgba(110, 185, 247, 0.42)",
    }));

    return { lineData, histogramData };
  }, [history]);
  const latestLegend = useMemo(() => getLatestLegend(chartData), [chartData]);
  const hasChartData = chartData.lineData.length > 0;

  loadingRef.current = isLoadingMore;
  hasMoreRef.current = hasMore;
  latestLegendRef.current = latestLegend;
  onLoadMoreRef.current = onLoadMore;

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }
    if (chartRef.current) {
      return;
    }

    const chart = createChart(containerRef.current, {
      height: 320,
      width: containerRef.current.clientWidth,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "rgba(255, 255, 255, 0.75)",
      },
      grid: {
        vertLines: { color: "rgba(255, 255, 255, 0.08)" },
        horzLines: { color: "rgba(255, 255, 255, 0.08)" },
      },
      rightPriceScale: { borderVisible: false },
      leftPriceScale: { visible: true, borderVisible: false },
      timeScale: { borderVisible: false },
    });

    const lineSeries = chart.addSeries(LineSeries, {
      color: "#6eb9f7",
      lineWidth: 2,
      priceScaleId: "right",
    });
    const histogramSeries = chart.addSeries(
      HistogramSeries,
      {
        priceFormat: { type: "volume" },
        priceScaleId: "left",
      },
      1,
    );

    lineSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.12, bottom: 0.16 },
    });
    histogramSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.72, bottom: 0 },
    });

    chartRef.current = chart;
    lineRef.current = lineSeries;
    histogramRef.current = histogramSeries;

    const resizeObserver = new ResizeObserver(([entry]) => {
      if (entry) {
        chart.applyOptions({ width: entry.contentRect.width });
      }
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      lineRef.current = null;
      histogramRef.current = null;
      didFitContentRef.current = false;
    };
  }, [hasChartData]);

  useEffect(() => {
    if (!chartRef.current || !lineRef.current || !histogramRef.current) {
      return;
    }

    justLoadedRef.current = true;
    lineRef.current.setData(chartData.lineData);
    histogramRef.current.setData(chartData.histogramData);

    if (chartData.lineData.length === 0) {
      didFitContentRef.current = false;
    } else if (!didFitContentRef.current) {
      chartRef.current.timeScale().fitContent();
      didFitContentRef.current = true;
    }

    setLegend(latestLegend);
  }, [chartData, latestLegend]);

  useEffect(() => {
    const chart = chartRef.current;
    const lineSeries = lineRef.current;
    const histogramSeries = histogramRef.current;

    if (!chart || !lineSeries || !histogramSeries) {
      return;
    }

    const handleCrosshairMove = (param: MouseEventParams<Time>) => {
      if (
        !param.time ||
        !param.seriesData.has(lineSeries) ||
        !param.seriesData.has(histogramSeries)
      ) {
        setLegend(latestLegendRef.current);
        return;
      }

      const lineData = param.seriesData.get(lineSeries) as LineData<Time>;
      const histogramData = param.seriesData.get(
        histogramSeries,
      ) as HistogramData<Time>;

      setLegend({
        marketCap: lineData.value,
        volume: histogramData.value,
        time: histogramData.time as UTCTimestamp,
      });
    };

    const handleTimeRangeChange = () => {
      if (justLoadedRef.current) {
        justLoadedRef.current = false;
        return;
      }

      if (loadingRef.current || !hasMoreRef.current) return;

      const logicalRange = chart.timeScale().getVisibleLogicalRange();
      if (logicalRange !== null && logicalRange.from < 10) {
        loadingRef.current = true;
        onLoadMoreRef.current();
      }
    };

    chart.subscribeCrosshairMove(handleCrosshairMove);
    chart.timeScale().subscribeVisibleTimeRangeChange(handleTimeRangeChange);
    return () => {
      chart.unsubscribeCrosshairMove(handleCrosshairMove);
      chart
        .timeScale()
        .unsubscribeVisibleTimeRangeChange(handleTimeRangeChange);
    };
  }, [hasChartData]);

  return (
    <section className="rounded-sm border border-secondary/35 bg-zinc-900 p-4 shadow-lg shadow-black/30">
      <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">Market History</h2>
          <p className="text-sm text-white/55">Market cap and hourly volume</p>
        </div>
        <div className="flex flex-wrap gap-3 text-sm text-white/70">
          <LegendValue
            label="Market cap"
            value={legend.marketCap}
            suffix={baseCurrencyText}
          />
          <LegendValue
            label="Volume"
            value={legend.volume}
            suffix={baseCurrencyText}
          />
          {legend.time && (
            <span className="text-white/50">{formatEpoch(legend.time)}</span>
          )}
        </div>
      </div>
      <div className="relative h-80">
        {hasChartData ? (
          <>
            {isLoadingMore && (
              <div className="absolute top-1/2 left-4 z-20 rounded-sm border border-secondary/30 bg-zinc-900/95 px-3 py-1 text-xs text-white/80">
                Loading older data...
              </div>
            )}
            <div ref={containerRef} className="h-full w-full" />
          </>
        ) : (
          <div className="flex h-80 items-center justify-center text-sm text-white/60">
            {getChartMessage({ isLoading, isError })}
          </div>
        )}
      </div>
    </section>
  );
}

function getChartMessage({
  isLoading,
  isError,
}: {
  isLoading: boolean;
  isError: boolean;
}) {
  if (isLoading) {
    return "Loading market history...";
  }

  if (isError) {
    return "Failed to load market history.";
  }

  return "No historical data available.";
}

function getLatestLegend(chartData: {
  lineData: LineData<Time>[];
  histogramData: HistogramData<Time>[];
}): LegendValues {
  const latestMarketCap = chartData.lineData.at(-1);
  const latestVolume = chartData.histogramData.at(-1);

  return {
    marketCap: latestMarketCap?.value,
    volume: latestVolume?.value,
    time: latestMarketCap?.time as UTCTimestamp | undefined,
  };
}

function LegendValue({
  label,
  value,
  suffix,
}: {
  label: string;
  value?: number;
  suffix: string;
}) {
  return (
    <span>
      <span className="text-white/45">{label}: </span>
      {value === undefined ? "N/A" : formatNumber(value)} {suffix}
    </span>
  );
}
