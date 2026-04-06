import { CircularProgress, Typography, Alert, Box, Paper } from "@mui/material";
import { useState, useEffect, useCallback } from "react";
import { UTCTimestamp } from "lightweight-charts";

import { useLeague } from "../../contexts/LeagueContext";
import type { CurrencyExchangeSnapshot } from "../../types";
import { Chart, ChartData } from "../Chart";
import { LegendData } from "../ItemHistoryChartLegend";
import { fetchSnapshotHistory as fetchSnapshotHistoryFromApi } from "./api";
import { SnapshotHistoryChartLegend } from "./SnapshotHistoryChartLegend";

export function SnapshotHistory({
  snapshot,
}: {
  snapshot: CurrencyExchangeSnapshot;
}) {
  const [chartData, setChartData] = useState<ChartData>({
    lineData: [],
    histogramData: [],
  });
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [oldestEpoch, setOldestEpoch] = useState<number | undefined>();
  const [legendData, setLegendData] = useState<LegendData>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { league, realm } = useLeague();

  useEffect(() => {
    const getHistory = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const historyDto = await fetchSnapshotHistoryFromApi(
          league.value,
          24 * 14,
        );

        setHasMore(historyDto.hasMore);

        if (historyDto.data.length > 0) {
          const reversedData = [...historyDto.data].reverse();
          setOldestEpoch(reversedData[0].epoch);

          const marketCaps = reversedData.map((entry) => ({
            time: entry.epoch as UTCTimestamp,
            value: entry.marketCap,
          }));
          const volumes = reversedData.map((entry) => ({
            time: entry.epoch as UTCTimestamp,
            value: entry.volume,
          }));
          setChartData({ lineData: marketCaps, histogramData: volumes });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred.");
      } finally {
        setIsLoading(false);
      }
    };

    getHistory();
  }, [league, snapshot.epoch]);

  const handleLoadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore || !oldestEpoch) {
      return;
    }

    setIsLoadingMore(true);
    try {
      const historyDto = await fetchSnapshotHistoryFromApi(
        league.value,
        24 * 14,
        oldestEpoch,
      );
      setHasMore(historyDto.hasMore);

      if (historyDto.data.length > 0) {
        const reversedData = [...historyDto.data].reverse();
        setOldestEpoch(reversedData[0].epoch);

        const newMarketCaps = reversedData.map((entry) => ({
          time: entry.epoch as UTCTimestamp,
          value: entry.marketCap,
        }));
        const newVolumes = reversedData.map((entry) => ({
          time: entry.epoch as UTCTimestamp,
          value: entry.volume,
        }));

        setChartData((prev) => ({
          lineData: [...newMarketCaps, ...prev.lineData],
          histogramData: [...newVolumes, ...prev.histogramData],
        }));
      }
    } catch (err) {
      console.error("Failed to load more data:", err);
    } finally {
      setIsLoadingMore(false);
    }
  }, [isLoadingMore, hasMore, oldestEpoch, league.value, realm?.value]);

  if (isLoading) {
    return (
      <Paper
        elevation={3}
        sx={{ p: 2, height: 450, display: "flex", flexDirection: "column" }}
      >
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100%",
          }}
        >
          <CircularProgress />
        </Box>
      </Paper>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (chartData.lineData.length > 0) {
    return (
      <Paper
        elevation={3}
        sx={{ p: 2, height: 375, display: "flex", flexDirection: "column" }}
      >
        <Box sx={{ position: "relative", height: "100%" }}>
          <Chart
            chartData={chartData}
            onLoadMore={handleLoadMore}
            hasMore={hasMore}
            isLoadingMore={isLoadingMore}
            onLegendDataChange={setLegendData}
            height={350}
          />
          <SnapshotHistoryChartLegend {...legendData} />
        </Box>
      </Paper>
    );
  }

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        height: 450,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Typography color="text.secondary">
        No historical data available.
      </Typography>
    </Paper>
  );
}

export default SnapshotHistory;
