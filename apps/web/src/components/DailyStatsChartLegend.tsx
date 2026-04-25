import { getCurrencyLabel } from "../currencyMeta";

export interface DailyStatsLegendData {
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  average?: number;
  time?: string;
}

interface DailyStatsChartLegendProps extends DailyStatsLegendData {
  baseCurrencyApiId: string;
  baseCurrencyText: string;
  textColor?: string;
}

const formatPrice = (value: number) =>
  value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

export const DailyStatsChartLegend = ({
  open,
  high,
  low,
  close,
  average,
  time,
  baseCurrencyApiId,
  baseCurrencyText,
  textColor = "white",
}: DailyStatsChartLegendProps) => {
  if (
    open === undefined &&
    high === undefined &&
    low === undefined &&
    close === undefined &&
    average === undefined &&
    time === undefined
  ) {
    return null;
  }

  const currencyText = getCurrencyLabel(baseCurrencyApiId, baseCurrencyText);

  return (
    <div
      style={{
        position: "absolute",
        top: 12,
        left: 75,
        zIndex: 10,
        color: textColor,
        fontFamily: "sans-serif",
        fontSize: "14px",
        pointerEvents: "none",
      }}
    >
      {time !== undefined && (
        <div style={{ color: "#aaa", marginBottom: "4px" }}>{time}</div>
      )}
      {open !== undefined &&
        high !== undefined &&
        low !== undefined &&
        close !== undefined && (
          <div>
            <span style={{ color: "#aaa" }}>O: </span>
            <strong>{formatPrice(open)}</strong>
            <span style={{ color: "#aaa" }}> H: </span>
            <strong>{formatPrice(high)}</strong>
            <span style={{ color: "#aaa" }}> L: </span>
            <strong>{formatPrice(low)}</strong>
            <span style={{ color: "#aaa" }}> C: </span>
            <strong>{formatPrice(close)}</strong>
            <span style={{ color: "#aaa" }}> {currencyText}</span>
          </div>
        )}
      {average !== undefined && (
        <div>
          <span style={{ color: "#aaa" }}>Average: </span>
          <strong>{formatPrice(average)}</strong>
          <span style={{ color: "#aaa" }}> {currencyText}</span>
        </div>
      )}
    </div>
  );
};
