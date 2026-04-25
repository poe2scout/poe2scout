import {
  CandlestickSeries,
  ColorType,
  createChart,
  HistogramSeries,
} from "lightweight-charts";
import type {
  CandlestickData,
  HistogramData,
  IChartApi,
  ISeriesApi,
  MouseEventParams,
  Time,
} from "lightweight-charts";
import { useEffect, useRef } from "react";

import type { DailyStatsLegendData } from "./DailyStatsChartLegend";

export interface DailyStatsChartData {
  candlestickData: CandlestickData<Time>[];
  histogramData: HistogramData<Time>[];
}

interface DailyStatsChartProps {
  chartData: DailyStatsChartData;
  colors?: {
    backgroundColor?: string;
    textColor?: string;
    gridColor?: string;
  };
  onLoadMore: () => void;
  hasMore: boolean;
  isLoadingMore: boolean;
  onLegendDataChange: (data: DailyStatsLegendData) => void;
  height: number;
}

export const DailyStatsChart = ({
  chartData,
  colors: {
    backgroundColor = "rgba(255, 255, 255, 0.0)",
    textColor = "white",
    gridColor = "#334158",
  } = {},
  onLoadMore,
  hasMore,
  isLoadingMore,
  onLegendDataChange,
  height,
}: DailyStatsChartProps) => {
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
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: backgroundColor },
        textColor,
      },
      rightPriceScale: { borderVisible: false },
      grid: { vertLines: { color: gridColor }, horzLines: { color: gridColor } },
      width: chartContainerRef.current.clientWidth,
      height,
      timeScale: { borderVisible: false },
    });

    chart.priceScale("right").applyOptions({
      scaleMargins: { top: 0.1, bottom: 0.25 },
    });

    chart.priceScale("left").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
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
    const volumeSeries = chart.addSeries(
      HistogramSeries,
      {
        color: "rgba(38, 166, 154, 0.45)",
        priceFormat: { type: "volume" },
        priceScaleId: "left",
      },
      1,
    );

    chartRef.current = chart;
    seriesRef.current = { candle: candleSeries, volume: volumeSeries };

    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current!.clientWidth });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartRef.current = null;
    };
  }, [backgroundColor, gridColor, height, textColor]);

  useEffect(() => {
    const chart = chartRef.current;
    const candleSeries = seriesRef.current.candle;
    const volumeSeries = seriesRef.current.volume;
    if (!chart || !candleSeries || !volumeSeries) return;

    const handleCrosshairMove = (param: MouseEventParams<Time>) => {
      const data = param.seriesData;
      if (!param.time || !data.has(candleSeries)) {
        const lastCandle =
          chartData.candlestickData[chartData.candlestickData.length - 1];
        const lastVolume =
          chartData.histogramData[chartData.histogramData.length - 1];
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

      const candleData = data.get(candleSeries) as CandlestickData<Time>;
      const volumeData = data.get(volumeSeries) as HistogramData<Time> | undefined;
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

    return () => {
      chart.timeScale().unsubscribeVisibleTimeRangeChange(handleTimeRangeChange);
    };
  }, [hasMore, onLoadMore]);

  useEffect(() => {
    justLoadedRef.current = true;

    seriesRef.current.candle?.setData(chartData.candlestickData);
    seriesRef.current.volume?.setData(chartData.histogramData);

    if (chartData.candlestickData.length > 0 && chartData.candlestickData.length <= 100) {
      chartRef.current?.timeScale().fitContent();
    }

    const lastCandle =
      chartData.candlestickData[chartData.candlestickData.length - 1];
    const lastVolume =
      chartData.histogramData[chartData.histogramData.length - 1];
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
    <>
      {isLoadingMore && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "20px",
            zIndex: 20,
            color: "white",
          }}
        >
          Loading...
        </div>
      )}
      <div ref={chartContainerRef} />
    </>
  );
};
