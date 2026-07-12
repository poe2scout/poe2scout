import type {
  CandlestickData,
  HistogramData,
  LineData,
  Time,
  UTCTimestamp,
} from "lightweight-charts";
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

export type ChartFrameProps = {
  height: number;
  hasMore: boolean;
  isLoadingMore: boolean;
  onLoadMore: () => void;
};

export const chartColors = {
  backgroundColor: "rgba(0, 0, 0, 0)",
  textColor: "rgba(255, 255, 255, 0.72)",
  gridColor: "rgba(110, 185, 247, 0.16)",
  lineColor: "#6eb9f7",
  volumeColor: "rgba(38, 166, 154, 0.72)",
};

export type ChartMode = "raw" | "daily";

export function getChartMode(
  value: string | null,
  defaultMode: ChartMode = "raw",
): ChartMode {
  if (value === "daily" || value === "raw") return value;
  return defaultMode;
}

export function ChartCanvas({
  containerRef,
  loading,
}: {
  containerRef: RefObject<HTMLDivElement | null>;
  loading: boolean;
}) {
  return (
    <>
      {loading && (
        <div className="absolute top-1/2 left-4 z-20 rounded-sm border border-secondary/30 bg-zinc-900/95 px-3 py-1 text-xs text-white/80">
          Loading older data...
        </div>
      )}
      <div ref={containerRef} className="h-full w-full" />
    </>
  );
}
