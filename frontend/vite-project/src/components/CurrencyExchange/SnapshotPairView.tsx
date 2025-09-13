import { useCallback, useEffect, useState } from "react";
import { SnapshotPair } from "./SnapshotPairList";
import { Alert, Box, CircularProgress, Paper, Typography } from "@mui/material";
import { useLeague } from "../../contexts/LeagueContext";
import { VITE_API_URL } from "./SnapshotHistory";
import { Chart, ChartData } from "../Chart";
import { LegendData } from "../ItemHistoryChartLegend";
import { UTCTimestamp } from "lightweight-charts";
import { SnapshotHistoryChartLegend } from "./SnapshotHistoryChartLegend";
import { useLocation, useOutletContext, useParams } from "react-router-dom";
import { CurrencyExchangeSnapshot } from "../../pages/CurrencyExchangePage";
import { PairChartLegendProps } from "./SnapshotPairChartLegend";

interface PairDataDetails {
    CurrencyItemId: number
    ValueTraded: number
    RelativePrice: number
    StockValue: number
    VolumeTraded: number
    HighestStock: number
}

interface PairData{
    CurrencyOneData: PairDataDetails
    CurrencyTwoData: PairDataDetails

}
interface GetCurrentSnapshotPairModel{
    Epoch: number
    Data: PairData
}

interface GetPairHistoryModel {
  History: GetCurrentSnapshotPairModel[]
  Meta: {
    hasMore: boolean
  }
}

const fetchPairHistory = async (currencyOneItemId: number, currencyTwoItemId: number, league: string, limit: number, endTime: number | null = null): Promise<GetPairHistoryModel> => {
  const url = endTime === null 
    ?`${VITE_API_URL}/currencyExchange/PairHistory?currencyOneItemId=${currencyOneItemId}&currencyTwoItemId=${currencyTwoItemId}&league=${league}&limit=${limit.toString()}` 
    : `${VITE_API_URL}/currencyExchange/PairHistory?currencyOneItemId=${currencyOneItemId}&currencyTwoItemId=${currencyTwoItemId}&league=${league}&limit=${limit.toString()}&endTime=${endTime}`

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch data: ${response.statusText}`);
  }
  return response.json();
};

export const SnapshotPairView = () => {
  const [itemOneChartData, setItemOneChartData] = useState<ChartData>({ lineData: [], histogramData: [] });
  const [itemTwoChartData, setItemTwoChartData] = useState<ChartData>({ lineData: [], histogramData: [] });
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [oldestEpoch, setOldestEpoch] = useState<number | undefined>();
  const [legendData, setLegendData] = useState<PairChartLegendProps>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { league } = useLeague();
  const params = useParams(); 

  useEffect(() => {
    const getHistory = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const pairHistoryData = await fetchPairHistory(currencyOneItemId, currencyTwoitemId, league.value, 24 * 14);

        setHasMore(pairHistoryData.Meta.hasMore);

        if (pairHistoryData.History && pairHistoryData.History.length > 0) {
          const reversedData = [...pairHistoryData.History].reverse();
          setOldestEpoch(reversedData[0].Epoch);

          const prices = reversedData.map(entry => ({
            time: entry.Epoch as UTCTimestamp,
            value: entry.Data.CurrencyOneData.VolumeTraded !== 0 ? entry.Data.CurrencyTwoData.VolumeTraded / entry.Data.CurrencyOneData.VolumeTraded: 0,
          }));
          const volumes = reversedData.map(entry => ({
            time: entry.Epoch as UTCTimestamp,
            value: entry.Data.CurrencyOneData.VolumeTraded,
          }));
          setItemOneChartData({ lineData: prices, histogramData: volumes });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred.");
      } finally {
        setIsLoading(false);
      }
    };
    getHistory();
  }, [league]);
    

  const handleLoadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore || !oldestEpoch) return;

    setIsLoadingMore(true);
    try {
      const pairHistoryData = await fetchPairHistory(currencyOneItemId, currencyTwoitemId, league.value, 24 * 14, oldestEpoch);
      setHasMore(pairHistoryData.Meta.hasMore);

      if (pairHistoryData.History && pairHistoryData.History.length > 0) {
        const reversedData = [...pairHistoryData.History].reverse();
        setOldestEpoch(reversedData[0].Epoch);

        const prices = reversedData.map(entry => ({
          time: entry.Epoch as UTCTimestamp,
          value: entry.Data.CurrencyTwoData.VolumeTraded / entry.Data.CurrencyOneData.VolumeTraded,
        }));
        const volumes = reversedData.map(entry => ({
          time: entry.Epoch as UTCTimestamp,
          value: entry.Data.CurrencyOneData.VolumeTraded,
        }));

        setItemOneChartData(prev => ({
          lineData: [...prices, ...prev.lineData],
          histogramData: [...volumes, ...prev.histogramData]}));
    }
    } catch (err) {
      console.error("Failed to load more data:", err);
    } finally {
      setIsLoadingMore(false);
    }
  }, [isLoadingMore, hasMore, oldestEpoch, league.value]);

  if (params?.currencyOneId === undefined || params?.currencyTwoId === undefined){
    return <Alert severity="error">Malformed currency item ids.</Alert>;
  }
  const currencyOneItemId = parseInt(params.currencyOneId, 10)
  const currencyTwoitemId = parseInt(params.currencyTwoId, 10)

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

  if (itemOneChartData.lineData.length > 0) {
    return (
      <Paper elevation={3} sx={{ p: 2, height: 375, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ position: 'relative', height: '100%' }}>
          <Chart
            chartData={itemOneChartData}
            onLoadMore={handleLoadMore}
            hasMore={hasMore}
            isLoadingMore={isLoadingMore}
            onLegendDataChange={(legendData) => {setLegendData(legendData.price, legendData.volume, legendData.time, currencyOneItemId, currencyTwoitemId )}}
            height={350}
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
