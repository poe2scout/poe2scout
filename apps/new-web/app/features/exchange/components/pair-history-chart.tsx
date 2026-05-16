import {
  ColorType,
  createChart,
  HistogramSeries,
  LineSeries,
  type HistogramData,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type MouseEventParams,
  type Time,
  type UTCTimestamp,
} from "lightweight-charts";
import { useEffect, useMemo, useRef, useState } from "react";
import type {
  ExchangePairHistoryEntry,
  ExchangePairHistoryMetricKey,
  ExchangePairHistoryMetricOption,
} from "../types";
import formatEpoch from "../utils/format-epoch";
import { formatPairHistoryMetric } from "./pair-history-metrics";

type LegendValues = {
  line?: number;
  volume?: number;
  time?: UTCTimestamp;
};

export default function PairHistoryChart({
  history,
  selectedOption,
  lineLabel,
  histogramLabel,
  hasMore,
  isLoadingMore,
  onLoadMore,
}: {
  history: ExchangePairHistoryEntry[];
  selectedOption: ExchangePairHistoryMetricOption;
  lineLabel: string;
  histogramLabel: string;
  hasMore: boolean;
  isLoadingMore: boolean;
  onLoadMore: () => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const lineRef = useRef<ISeriesApi<"Line"> | null>(null);
  const histogramRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const loadingRef = useRef(false);
  const justLoadedRef = useRef(false);
  const [legend, setLegend] = useState<LegendValues>({});

  const chartData = useMemo(() => {
    const ordered = [...history].sort((a, b) => a.epoch - b.epoch);
    const lineData = ordered.flatMap((entry): LineData<Time>[] => {
      const value =
        entry.data[selectedOption.dataKey][selectedOption.metricKey];

      if (!Number.isFinite(value)) {
        return [];
      }

      return [
        {
          time: entry.epoch as UTCTimestamp,
          value,
        },
      ];
    });
    const histogramData: HistogramData<Time>[] = ordered.map((entry) => ({
      time: entry.epoch as UTCTimestamp,
      value: entry.data[selectedOption.dataKey].volumeTraded,
      color: "rgba(38, 166, 154, 0.72)",
    }));

    return { lineData, histogramData };
  }, [history, selectedOption]);

  useEffect(() => {
    loadingRef.current = isLoadingMore;
  }, [isLoadingMore]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "rgba(255, 255, 255, 0.72)",
      },
      rightPriceScale: { borderVisible: false },
      leftPriceScale: { visible: true, borderVisible: false },
      grid: {
        vertLines: { color: "rgba(110, 185, 247, 0.16)" },
        horzLines: { color: "rgba(110, 185, 247, 0.16)" },
      },
      width: container.clientWidth,
      height: 500,
      timeScale: { borderVisible: false },
    });

    const lineSeries = chart.addSeries(LineSeries, {
      priceScaleId: "right",
      color: "#6eb9f7",
      lineWidth: 2,
    });
    lineSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.12, bottom: 0.18 },
    });

    const histogramSeries = chart.addSeries(
      HistogramSeries,
      {
        priceFormat: { type: "volume" },
        priceScaleId: "left",
      },
      1,
    );
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
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      lineRef.current = null;
      histogramRef.current = null;
    };
  }, []);

  useEffect(() => {
    const chart = chartRef.current;
    const lineSeries = lineRef.current;
    const histogramSeries = histogramRef.current;
    if (!chart || !lineSeries || !histogramSeries) return;

    const handleCrosshairMove = (param: MouseEventParams<Time>) => {
      if (!param.time || !param.seriesData.has(lineSeries)) {
        setLegend(getLatestLegend(chartData));
        return;
      }

      const lineData = param.seriesData.get(lineSeries) as LineData<Time>;
      const histogramData = param.seriesData.get(histogramSeries) as
        | HistogramData<Time>
        | undefined;

      setLegend({
        line: lineData.value,
        volume: histogramData?.value,
        time: lineData.time as UTCTimestamp,
      });
    };

    chart.subscribeCrosshairMove(handleCrosshairMove);
    return () => chart.unsubscribeCrosshairMove(handleCrosshairMove);
  }, [chartData]);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;

    const handleTimeRangeChange = () => {
      if (justLoadedRef.current) {
        justLoadedRef.current = false;
        return;
      }

      if (loadingRef.current || !hasMore) return;

      const logicalRange = chart.timeScale().getVisibleLogicalRange();
      if (logicalRange !== null && logicalRange.from < 10) {
        loadingRef.current = true;
        onLoadMore();
      }
    };

    chart.timeScale().subscribeVisibleTimeRangeChange(handleTimeRangeChange);
    return () =>
      chart
        .timeScale()
        .unsubscribeVisibleTimeRangeChange(handleTimeRangeChange);
  }, [hasMore, onLoadMore]);

  useEffect(() => {
    justLoadedRef.current = true;
    lineRef.current?.setData(chartData.lineData);
    histogramRef.current?.setData(chartData.histogramData);

    if (chartData.lineData.length > 0 && chartData.lineData.length <= 100) {
      chartRef.current?.timeScale().fitContent();
    }

    setLegend(getLatestLegend(chartData));
  }, [chartData]);

  if (chartData.lineData.length === 0) {
    return (
      <div className="flex h-125 items-center justify-center text-sm text-white/60">
        No historical data is available for this pair.
      </div>
    );
  }

  return (
    <div className="relative h-125 w-full">
      {isLoadingMore && (
        <div className="absolute top-1/2 left-4 z-20 rounded-sm border border-secondary/30 bg-zinc-900/95 px-3 py-1 text-xs text-white/80">
          Loading older data...
        </div>
      )}
      <PairHistoryLegend
        data={legend}
        metric={selectedOption.metricKey}
        lineLabel={lineLabel}
        histogramLabel={histogramLabel}
      />
      <div ref={containerRef} className="h-full w-full" />
    </div>
  );
}

function PairHistoryLegend({
  data,
  metric,
  lineLabel,
  histogramLabel,
}: {
  data: LegendValues;
  metric: ExchangePairHistoryMetricKey;
  lineLabel: string;
  histogramLabel: string;
}) {
  if (
    data.line === undefined &&
    data.volume === undefined &&
    data.time === undefined
  ) {
    return null;
  }

  return (
    <div className="pointer-events-none absolute top-3 left-16 z-10 max-w-[calc(100%-4rem)] text-sm text-white">
      {data.line !== undefined && (
        <div>
          <span className="text-white/55">{lineLabel}: </span>
          <strong>{formatPairHistoryMetric(metric, data.line)}</strong>
        </div>
      )}
      {data.volume !== undefined && (
        <div>
          <span className="text-white/55">{histogramLabel}: </span>
          <strong>
            {formatPairHistoryMetric("volumeTraded", data.volume)}
          </strong>
        </div>
      )}
      {data.time !== undefined && (
        <div className="mt-1 text-white/55">{formatEpoch(data.time)}</div>
      )}
    </div>
  );
}

function getLatestLegend(chartData: {
  lineData: LineData<Time>[];
  histogramData: HistogramData<Time>[];
}): LegendValues {
  const latestLine = chartData.lineData.at(-1);
  const latestVolume = chartData.histogramData.at(-1);

  return {
    line: latestLine?.value,
    volume: latestVolume?.value,
    time: latestLine?.time as UTCTimestamp | undefined,
  };
}
