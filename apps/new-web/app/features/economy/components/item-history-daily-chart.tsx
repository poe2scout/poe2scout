import { useEffect, useRef } from "react";
import {
  ChartCanvas,
  chartColors,
  type ChartFrameProps,
  type DailyChartData,
  type DailyLegendData,
} from "./item-history-charts";
import {
  type IChartApi,
  createChart,
  ColorType,
  CandlestickSeries,
  HistogramSeries,
  type MouseEventParams,
  type CandlestickData,
  type HistogramData,
  type ISeriesApi,
  type Time,
} from "lightweight-charts";

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
