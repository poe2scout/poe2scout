import { useEffect, useRef } from "react";
import {
  ChartCanvas,
  chartColors,
  type ChartFrameProps,
  type RawChartData,
  type RawLegendData,
} from "./item-history-charts";
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
