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
}: {
  history: ExchangeSnapshot[];
  baseCurrencyText: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const lineRef = useRef<ISeriesApi<"Line"> | null>(null);
  const histogramRef = useRef<ISeriesApi<"Histogram"> | null>(null);
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

  useEffect(() => {
    if (!containerRef.current) {
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
    };
  }, []);

  useEffect(() => {
    if (!chartRef.current || !lineRef.current || !histogramRef.current) {
      return;
    }

    lineRef.current.setData(chartData.lineData);
    histogramRef.current.setData(chartData.histogramData);
    chartRef.current.timeScale().fitContent();

    const lastMarketCap = chartData.lineData.at(-1);
    const lastVolume = chartData.histogramData.at(-1);
    setLegend({
      marketCap: lastMarketCap?.value,
      volume: lastVolume?.value,
      time: lastVolume?.time as UTCTimestamp | undefined,
    });
  }, [chartData]);

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

    chart.subscribeCrosshairMove(handleCrosshairMove);

    return () => chart.unsubscribeCrosshairMove(handleCrosshairMove);
  }, [chartData]);

  return (
    <section className="rounded-sm border border-secondary/35 bg-zinc-950 p-4 shadow-lg shadow-black/30">
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
      {chartData.lineData.length > 0 ? (
        <div className="relative h-80">
          <div ref={containerRef} className="h-full w-full" />
        </div>
      ) : (
        <div className="flex h-80 items-center justify-center text-sm text-white/60">
          No historical data available.
        </div>
      )}
    </section>
  );
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
