import {
  CandlestickSeries,
  ColorType,
  createChart,
  HistogramSeries,
  LineSeries,
} from "lightweight-charts";
import type {
  CandlestickData,
  HistogramData,
  IChartApi,
  ISeriesApi,
  LineData,
  MouseEventParams,
  Time,
  UTCTimestamp,
} from "lightweight-charts";
import { useEffect, useRef } from "react";
import type { RefObject } from "react";

export type RawChartData = {
  lineData: LineData<Time>[];
  histogramData: HistogramData<Time>[];
};

export type RawLegendData = {
  price?: number;
  volume?: number;
  time?: UTCTimestamp;
};

export type DailyChartData = {
  candlestickData: CandlestickData<Time>[];
  histogramData: HistogramData<Time>[];
};

export type DailyLegendData = {
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  average?: number;
  volume?: number;
  time?: string;
};

type ChartFrameProps = {
  height: number;
  hasMore: boolean;
  isLoadingMore: boolean;
  onLoadMore: () => void;
};

const chartColors = {
  backgroundColor: "rgba(0, 0, 0, 0)",
  textColor: "rgba(255, 255, 255, 0.72)",
  gridColor: "rgba(110, 185, 247, 0.16)",
  lineColor: "#6eb9f7",
  volumeColor: "rgba(38, 166, 154, 0.72)",
};

export function RawPriceChart({
  chartData,
  height,
  hasMore,
  isLoadingMore,
  onLoadMore,
  onLegendDataChange,
}: ChartFrameProps & {
  chartData: RawChartData;
  onLegendDataChange: (data: RawLegendData) => void;
}) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<{
    line: ISeriesApi<"Line"> | null;
    volume: ISeriesApi<"Histogram"> | null;
  }>({ line: null, volume: null });
  const loadingRef = useRef(false);
  const justLoadedRef = useRef(false);

  useEffect(() => {
    loadingRef.current = isLoadingMore;
  }, [isLoadingMore]);

  useEffect(() => {
    const container = chartContainerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      layout: {
        background: {
          type: ColorType.Solid,
          color: chartColors.backgroundColor,
        },
        textColor: chartColors.textColor,
      },
      rightPriceScale: { borderVisible: false },
      leftPriceScale: { visible: true, borderVisible: false },
      grid: {
        vertLines: { color: chartColors.gridColor },
        horzLines: { color: chartColors.gridColor },
      },
      width: container.clientWidth,
      height,
      timeScale: { borderVisible: false },
    });

    const lineSeries = chart.addSeries(LineSeries, {
      priceScaleId: "right",
      color: chartColors.lineColor,
    });
    lineSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.15, bottom: 0.15 },
    });

    const volumeSeries = chart.addSeries(
      HistogramSeries,
      {
        color: chartColors.volumeColor,
        priceFormat: { type: "volume" },
        priceScaleId: "left",
      },
      1,
    );

    chartRef.current = chart;
    seriesRef.current = { line: lineSeries, volume: volumeSeries };

    const resizeObserver = new ResizeObserver(([entry]) => {
      chart.applyOptions({ width: entry.contentRect.width });
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [height]);

  useEffect(() => {
    const chart = chartRef.current;
    const lineSeries = seriesRef.current.line;
    const volumeSeries = seriesRef.current.volume;
    if (!chart || !lineSeries || !volumeSeries) return;

    const handleCrosshairMove = (param: MouseEventParams<Time>) => {
      const seriesData = param.seriesData;
      if (!param.time || !seriesData.has(lineSeries)) {
        const lastPrice = chartData.lineData.at(-1);
        const lastVolume = chartData.histogramData.at(-1);
        onLegendDataChange({
          price: lastPrice?.value,
          volume: lastVolume?.value,
          time: lastVolume?.time as UTCTimestamp | undefined,
        });
        return;
      }

      const priceData = seriesData.get(lineSeries) as LineData<Time>;
      const volumeData = seriesData.get(volumeSeries) as
        | HistogramData<Time>
        | undefined;
      onLegendDataChange({
        price: priceData.value,
        volume: volumeData?.value,
        time: priceData.time as UTCTimestamp,
      });
    };

    chart.subscribeCrosshairMove(handleCrosshairMove);
    return () => chart.unsubscribeCrosshairMove(handleCrosshairMove);
  }, [chartData, onLegendDataChange]);

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
    seriesRef.current.line?.setData(chartData.lineData);
    seriesRef.current.volume?.setData(chartData.histogramData);

    if (chartData.lineData.length > 0 && chartData.lineData.length <= 100) {
      chartRef.current?.timeScale().fitContent();
    }

    const lastPrice = chartData.lineData.at(-1);
    const lastVolume = chartData.histogramData.at(-1);
    onLegendDataChange({
      price: lastPrice?.value,
      volume: lastVolume?.value,
      time: lastVolume?.time as UTCTimestamp | undefined,
    });
  }, [chartData, onLegendDataChange]);

  return (
    <ChartCanvas containerRef={chartContainerRef} loading={isLoadingMore} />
  );
}

export function DailyStatsChart({
  chartData,
  height,
  hasMore,
  isLoadingMore,
  onLoadMore,
  onLegendDataChange,
}: ChartFrameProps & {
  chartData: DailyChartData;
  onLegendDataChange: (data: DailyLegendData) => void;
}) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<{
    candle: ISeriesApi<"Candlestick"> | null;
    volume: ISeriesApi<"Histogram"> | null;
  }>({ candle: null, volume: null });
  const loadingRef = useRef(false);
  const justLoadedRef = useRef(false);

  useEffect(() => {
    loadingRef.current = isLoadingMore;
  }, [isLoadingMore]);

  useEffect(() => {
    const container = chartContainerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      layout: {
        background: {
          type: ColorType.Solid,
          color: chartColors.backgroundColor,
        },
        textColor: chartColors.textColor,
      },
      rightPriceScale: { borderVisible: false },
      leftPriceScale: { visible: true, borderVisible: false },
      grid: {
        vertLines: { color: chartColors.gridColor },
        horzLines: { color: chartColors.gridColor },
      },
      width: container.clientWidth,
      height,
      timeScale: { borderVisible: false },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      priceScaleId: "right",
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderUpColor: "#26a69a",
      borderDownColor: "#ef5350",
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });
    candleSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.15, bottom: 0.15 },
    });

    const volumeSeries = chart.addSeries(
      HistogramSeries,
      {
        color: chartColors.volumeColor,
        priceFormat: { type: "volume" },
        priceScaleId: "left",
      },
      1,
    );

    chartRef.current = chart;
    seriesRef.current = { candle: candleSeries, volume: volumeSeries };

    const resizeObserver = new ResizeObserver(([entry]) => {
      chart.applyOptions({ width: entry.contentRect.width });
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [height]);

  useEffect(() => {
    const chart = chartRef.current;
    const candleSeries = seriesRef.current.candle;
    const volumeSeries = seriesRef.current.volume;
    if (!chart || !candleSeries || !volumeSeries) return;

    const handleCrosshairMove = (param: MouseEventParams<Time>) => {
      const seriesData = param.seriesData;
      if (!param.time || !seriesData.has(candleSeries)) {
        const lastCandle = chartData.candlestickData.at(-1);
        const lastVolume = chartData.histogramData.at(-1);
        onLegendDataChange({
          open: lastCandle?.open,
          high: lastCandle?.high,
          low: lastCandle?.low,
          close: lastCandle?.close,
          volume: lastVolume?.value,
          time: lastCandle?.time?.toString(),
        });
        return;
      }

      const candleData = seriesData.get(candleSeries) as CandlestickData<Time>;
      const volumeData = seriesData.get(volumeSeries) as
        | HistogramData<Time>
        | undefined;
      onLegendDataChange({
        open: candleData.open,
        high: candleData.high,
        low: candleData.low,
        close: candleData.close,
        volume: volumeData?.value,
        time: candleData.time.toString(),
      });
    };

    chart.subscribeCrosshairMove(handleCrosshairMove);
    return () => chart.unsubscribeCrosshairMove(handleCrosshairMove);
  }, [chartData, onLegendDataChange]);

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
    seriesRef.current.candle?.setData(chartData.candlestickData);
    seriesRef.current.volume?.setData(chartData.histogramData);

    if (
      chartData.candlestickData.length > 0 &&
      chartData.candlestickData.length <= 100
    ) {
      chartRef.current?.timeScale().fitContent();
    }

    const lastCandle = chartData.candlestickData.at(-1);
    const lastVolume = chartData.histogramData.at(-1);
    onLegendDataChange({
      open: lastCandle?.open,
      high: lastCandle?.high,
      low: lastCandle?.low,
      close: lastCandle?.close,
      volume: lastVolume?.value,
      time: lastCandle?.time?.toString(),
    });
  }, [chartData, onLegendDataChange]);

  return (
    <ChartCanvas containerRef={chartContainerRef} loading={isLoadingMore} />
  );
}

function ChartCanvas({
  containerRef,
  loading,
}: {
  containerRef: RefObject<HTMLDivElement | null>;
  loading: boolean;
}) {
  return (
    <>
      {loading && (
        <div className="absolute top-1/2 left-4 z-20 rounded-sm border border-secondary/30 bg-zinc-950/90 px-3 py-1 text-xs text-white/80">
          Loading older data...
        </div>
      )}
      <div ref={containerRef} className="h-full w-full" />
    </>
  );
}
