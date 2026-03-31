import { memo, useCallback, useState } from "react";
import {
  Box,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import type { SelectChangeEvent } from "@mui/material/Select";

import { Chart, ChartData } from "../../Chart";
import PairHistoryChartLegend from "../PairHistoryChartLegend";
import type { LegendData } from "../../ItemHistoryChartLegend";
import { formatMetricValue } from "./metricFormatters";
import type { MetricMenuOption, MetricKey } from "./metricTypes";

interface PairHistoryChartSectionProps {
  chartData: ChartData;
  hasMore: boolean;
  isLoadingMore: boolean;
  onLoadMore: () => void;
  metricOptions: MetricMenuOption[];
  selectedMetricId: string;
  onMetricChange: (event: SelectChangeEvent) => void;
  selectedMetricKey: MetricKey;
  legendLineLabel: string;
  legendHistogramLabel: string;
}

const PairHistoryChartSection = memo(
  ({
    chartData,
    hasMore,
    isLoadingMore,
    onLoadMore,
    metricOptions,
    selectedMetricId,
    onMetricChange,
    selectedMetricKey,
    legendLineLabel,
    legendHistogramLabel,
  }: PairHistoryChartSectionProps) => {
    const [legendData, setLegendData] = useState<LegendData>({});

    const handleLegendChange = useCallback((data: LegendData) => {
      setLegendData((prev) => {
        if (
          prev.price === data.price &&
          prev.volume === data.volume &&
          prev.time === data.time
        ) {
          return prev;
        }
        return data;
      });
    }, []);

    const selectValue = selectedMetricId || (metricOptions[0]?.id ?? "");

    const lineFormatter = useCallback(
      (value: number) => formatMetricValue(selectedMetricKey, value),
      [selectedMetricKey],
    );

    const histogramFormatter = useCallback(
      (value: number) => formatMetricValue("VolumeTraded", value),
      [],
    );

    return (
      <Paper elevation={3} sx={{ p: 2 }}>
        <Stack spacing={2}>
          <Stack
            direction={{ xs: "column", sm: "row" }}
            spacing={2}
            alignItems={{ xs: "stretch", sm: "center" }}
          >
            <FormControl size="small" sx={{ minWidth: 220 }}>
              <InputLabel id="metric-select-label">Metric</InputLabel>
              <Select
                labelId="metric-select-label"
                value={selectValue}
                label="Metric"
                onChange={onMetricChange}
              >
                {metricOptions.map((option) => (
                  <MenuItem key={option.id} value={option.id}>
                    {option.menuLabel}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>

          {chartData.lineData.length > 0 ? (
            <Box sx={{ position: "relative", height: 380 }}>
              <Chart
                chartData={chartData}
                onLoadMore={onLoadMore}
                hasMore={hasMore}
                isLoadingMore={isLoadingMore}
                onLegendDataChange={handleLegendChange}
                height={360}
              />
              <PairHistoryChartLegend
                {...legendData}
                lineLabel={legendLineLabel}
                histogramLabel={legendHistogramLabel}
                lineFormatter={lineFormatter}
                histogramFormatter={histogramFormatter}
              />
            </Box>
          ) : (
            <Box
              sx={{
                height: 320,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Typography color="text.secondary">
                No historical data available for this pair.
              </Typography>
            </Box>
          )}
        </Stack>
      </Paper>
    );
  },
);

PairHistoryChartSection.displayName = "PairHistoryChartSection";

export default PairHistoryChartSection;
