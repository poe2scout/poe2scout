import { memo } from "react";
import { LegendData } from "../ItemHistoryChartLegend";
import { FormatTimeFromEpoch } from "../FormatTime";

interface PairHistoryChartLegendProps extends LegendData {
  lineLabel: string;
  histogramLabel: string;
  lineFormatter?: (value: number) => string;
  histogramFormatter?: (value: number) => string;
}

export const PairHistoryChartLegend = memo(({
  price,
  volume,
  time,
  lineLabel,
  histogramLabel,
  lineFormatter,
  histogramFormatter,
}: PairHistoryChartLegendProps) => {
  if (price === undefined && volume === undefined && time === undefined) {
    return null;
  }

  const formatLineValue = (value: number) =>
    lineFormatter ? lineFormatter(value) : value.toLocaleString();
  const formatHistogramValue = (value: number) =>
    histogramFormatter ? histogramFormatter(value) : value.toLocaleString();

  return (
    <div
      style={{
        position: "absolute",
        top: 8,
        left: 12,
        zIndex: 10,
        fontFamily: "sans-serif",
        fontSize: "13px",
        pointerEvents: "none",
      }}
    >
      {price !== undefined && (
        <div>
          <span style={{ color: "#aaa" }}>{lineLabel}: </span>
          <strong style={{ color: "white" }}>{formatLineValue(price)}</strong>
        </div>
      )}
      {volume !== undefined && (
        <div>
          <span style={{ color: "#aaa" }}>{histogramLabel}: </span>
          <strong style={{ color: "white" }}>{formatHistogramValue(volume)}</strong>
        </div>
      )}
      {time !== undefined && (
        <div style={{ color: "#aaa", marginTop: "4px" }}>
          {FormatTimeFromEpoch(time as number)}
        </div>
      )}
    </div>
  );
});

PairHistoryChartLegend.displayName = "PairHistoryChartLegend";

export default PairHistoryChartLegend;
