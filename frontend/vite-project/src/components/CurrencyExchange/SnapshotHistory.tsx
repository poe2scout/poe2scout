import { CircularProgress, Typography, Alert, Box, Paper } from "@mui/material";
import { useState, useEffect, useCallback } from "react";
import { CurrencyExchangeSnapshot } from "../../pages/CurrencyExchangePage";
import { useLeague } from "../../contexts/LeagueContext";
import { UTCTimestamp } from "lightweight-charts";
import { Chart, ChartData } from "../Chart";
import { SnapshotHistoryChartLegend } from "./SnapshotHistoryChartLegend";
import { LegendData } from "../ItemHistoryChartLegend";

const uri = import.meta.env.VITE_API_URL;

interface SnapshotHistoryDto {
  Data: CurrencyExchangeSnapshot[]
  Meta: {
    hasMore: boolean
  }
}

const fetchCurrencyExchangeSnapshotHistory = async (league: string, limit: number, endTime: number | null = null): Promise<SnapshotHistoryDto> => {
  const url = endTime === null 
    ?`${uri}/currencyExchange/SnapshotHistory?league=${league}&limit=${limit.toString()}` 
    : `${uri}/currencyExchange/SnapshotHistory?league=${league}&limit=${limit.toString()}&endTime=${endTime}`

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch data: ${response.statusText}`);
  }
  return response.json();
};

export function SnapshotHistory({ snapshot }: { snapshot: CurrencyExchangeSnapshot }) {
  const [chartData, setChartData] = useState<ChartData>({ lineData: [], histogramData: [] });
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [oldestEpoch, setOldestEpoch] = useState<number | undefined>();
  const [legendData, setLegendData] = useState<LegendData>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { league } = useLeague();

  useEffect(() => {
    const getHistory = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const historyDto = await fetchCurrencyExchangeSnapshotHistory(league.value, 24 * 14);

        setHasMore(historyDto.Meta.hasMore);

        if (historyDto.Data && historyDto.Data.length > 0) {
            const reversedData = [...historyDto.Data].reverse();
            setOldestEpoch(reversedData[0].Epoch);

            const marketCaps = reversedData.map(entry => ({
                time: entry.Epoch as UTCTimestamp,
                value: entry.MarketCap,
            }));
            const volumes = reversedData.map(entry => ({
                time: entry.Epoch as UTCTimestamp,
                value: entry.Volume,
            }));
            setChartData({ lineData: volumes, histogramData: marketCaps });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred.");
      } finally {
        setIsLoading(false);
      }
    };
    getHistory();
  }, [league, snapshot.Epoch]);

  const handleLoadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore || !oldestEpoch) return;

    setIsLoadingMore(true);
    try {
      const historyDto = await fetchCurrencyExchangeSnapshotHistory(league.value, 24 * 14, oldestEpoch);
      setHasMore(historyDto.Meta.hasMore);

      if (historyDto.Data && historyDto.Data.length > 0) {
        const reversedData = [...historyDto.Data].reverse();
        setOldestEpoch(reversedData[0].Epoch);

        const newMarketCaps = reversedData.map(entry => ({
            time: entry.Epoch as UTCTimestamp,
            value: entry.MarketCap,
        }));
        const newVolumes = reversedData.map(entry => ({
            time: entry.Epoch as UTCTimestamp,
            value: entry.Volume,
        }));

        setChartData(prev => ({
            lineData: [...newVolumes, ...prev.lineData],
            histogramData: [...newMarketCaps, ...prev.histogramData],
        }));
      }
    } catch (err) {
      console.error("Failed to load more data:", err);
    } finally {
      setIsLoadingMore(false);
    }
  }, [isLoadingMore, hasMore, oldestEpoch, league.value]);

  if (isLoading) {
    return (
      <Paper elevation={3} sx={{ p: 2, height: 450, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100%'
        }}>
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
      <Paper elevation={3} sx={{ p: 2, height: 450, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ position: 'relative', height: '100%' }}>
          <Chart
            chartData={chartData}
            onLoadMore={handleLoadMore}
            hasMore={hasMore}
            isLoadingMore={isLoadingMore}
            onLegendDataChange={setLegendData}
            height={425}
          />
          <SnapshotHistoryChartLegend {...legendData} />
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 2, height: 450, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Typography color="text.secondary">No historical data available.</Typography>
    </Paper>
  );
}

export default SnapshotHistory;