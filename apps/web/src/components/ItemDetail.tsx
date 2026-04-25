import { useEffect, useState, useMemo, useCallback, useRef } from "react";
import type { MouseEvent } from "react";
import {
  Box,
  Button,
  CircularProgress,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import { ItemName } from "./TableColumnComponents/ItemName";
import type { ApiItem } from "../types";
import { useLanguage } from "../contexts/LanguageContext";
import translations from "../translationskrmapping.json";
import { useLeague } from "../contexts/LeagueContext";
import type {
  DailyStatEntry,
  ItemDailyStatsHistoryResponse,
  ItemHistoryResponse,
  PriceLogEntry,
} from "../types";
import { Chart } from "./Chart";
import { UTCTimestamp } from "lightweight-charts";
import ReferenceCurrencySelector, { type BaseCurrencies } from "./ReferenceCurrencySelector";
import { ChartLegend, type LegendData } from "./ItemHistoryChartLegend";
import { fetchItemDailyStatsHistory, fetchItemHistory } from "../api/economy";
import { getCurrencyLabel } from "../currencyMeta";
import { DailyStatsChart } from "./DailyStatsChart";
import type { DailyStatsChartData } from "./DailyStatsChart";
import {
  DailyStatsChartLegend,
} from "./DailyStatsChartLegend";
import type { DailyStatsLegendData } from "./DailyStatsChartLegend";

const DetailContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
}));

const HeaderContainer = styled(Box)({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "24px",
});

interface ItemDetailProps {
  item: ApiItem;
  onBack: () => void;
  initialReferenceCurrency: string;
  referenceCurrencyOptions: string[];
}

type ChartMode = "recent" | "daily";
const DAILY_CHART_SEEN_STORAGE_KEY = "poe2scout.dailyChartSeen";

export function ItemDetail({
  item,
  onBack,
  initialReferenceCurrency,
  referenceCurrencyOptions,
}: ItemDetailProps) {
  const logCountRef = useRef<number>(14 * 24);
  const [history, setHistory] = useState<PriceLogEntry[]>([]);
  const [dailyStats, setDailyStats] = useState<DailyStatEntry[]>([]);

  const [hasMore, setHasMore] = useState(true);
  const [dailyHasMore, setDailyHasMore] = useState(true);
  const [oldestTimestamp, setOldestTimestamp] = useState<string>(() => new Date().toISOString());
  const [oldestDailyDate, setOldestDailyDate] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false); 
  const [isDailyLoading, setIsDailyLoading] = useState(false);
  const [isDailyLoadingMore, setIsDailyLoadingMore] = useState(false);
  const [legendData, setLegendData] = useState<LegendData>({});
  const [dailyLegendData, setDailyLegendData] = useState<DailyStatsLegendData>({});
  const [chartMode, setChartMode] = useState<ChartMode>("recent");
  const [showDailyNewBadge, setShowDailyNewBadge] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.localStorage.getItem(DAILY_CHART_SEEN_STORAGE_KEY) !== "true";
  });

  const [selectedReference, setSelectedReference] = useState<BaseCurrencies>(initialReferenceCurrency);
  const { language } = useLanguage();
  const { league } = useLeague();

  const fetchPriceHistory = useCallback(async (isInitialLoad: boolean, cursor: string) => {
    if (isInitialLoad) {
        setIsLoading(true);
    } else {
        setIsLoadingMore(true);
    }
    
    try {
      const data: ItemHistoryResponse = await fetchItemHistory({
        itemId: item.itemId,
        leagueName: league.value,
        logCount: logCountRef.current,
        referenceCurrency: selectedReference,
        endTime: cursor,
      });

      const reversedData = [...data.priceHistory].reverse();

      setHistory(prevHistory => isInitialLoad ? reversedData : [...reversedData, ...prevHistory]);
      setHasMore(data.hasMore);

      if (data.priceHistory.length > 0) {
        setOldestTimestamp(reversedData[0].time);
      }
    } catch (error) {
      console.error("Error fetching price history:", error);
      setHistory([]); // Reset on error
    } finally {
      if (isInitialLoad) setIsLoading(false);
      else setIsLoadingMore(false);
      logCountRef.current = logCountRef.current * 2;
    }
  }, [item.itemId, league.value, selectedReference]);

  const fetchDailyStats = useCallback(async (isInitialLoad: boolean, cursor?: string) => {
    if (isInitialLoad) {
      setIsDailyLoading(true);
    } else {
      setIsDailyLoadingMore(true);
    }

    try {
      const data: ItemDailyStatsHistoryResponse = await fetchItemDailyStatsHistory({
        itemId: item.itemId,
        leagueName: league.value,
        dayCount: 90,
        endDate: cursor,
      });

      setDailyStats((prevDailyStats) => {
        if (isInitialLoad) return data.dailyStats;

        const existingTimes = new Set(prevDailyStats.map((entry) => entry.time));
        const olderStats = data.dailyStats.filter(
          (entry) => !existingTimes.has(entry.time),
        );
        return [...olderStats, ...prevDailyStats];
      });
      setDailyHasMore(data.hasMore);

      if (data.dailyStats.length > 0) {
        setOldestDailyDate(data.dailyStats[0].time);
      }
    } catch (error) {
      console.error("Error fetching daily stat history:", error);
      setDailyStats([]);
    } finally {
      if (isInitialLoad) setIsDailyLoading(false);
      else setIsDailyLoadingMore(false);
    }
  }, [item.itemId, league.value]);

  useEffect(() => {
    if (chartMode !== "recent") return;

    setHistory([]); 
    setHasMore(true);
    const initialCursor = new Date().toISOString();
    setOldestTimestamp(initialCursor);
    logCountRef.current = 14 * 24; 

    fetchPriceHistory(true, initialCursor);
  }, [item.id, selectedReference, fetchPriceHistory, chartMode]);

  useEffect(() => {
    if (chartMode !== "daily") return;

    setDailyStats([]);
    setDailyHasMore(true);
    setOldestDailyDate(undefined);
    fetchDailyStats(true);
  }, [item.id, fetchDailyStats, chartMode]);

  const handleLoadMore = useCallback(() => {
    if (!isLoadingMore && hasMore) {
        fetchPriceHistory(false, oldestTimestamp);
    }
  }, [isLoadingMore, hasMore, oldestTimestamp, fetchPriceHistory]);

  const handleDailyLoadMore = useCallback(() => {
    if (!isDailyLoadingMore && dailyHasMore && oldestDailyDate) {
      fetchDailyStats(false, oldestDailyDate);
    }
  }, [dailyHasMore, fetchDailyStats, isDailyLoadingMore, oldestDailyDate]);

  const onSelectedReferenceChange = (newReference: BaseCurrencies) => {
    setSelectedReference(newReference);
  };

  const handleChartModeChange = (
    _: MouseEvent<HTMLElement>,
    newMode: ChartMode | null,
  ) => {
    if (newMode !== null) {
      setChartMode(newMode);
      if (newMode === "daily" && showDailyNewBadge) {
        window.localStorage.setItem(DAILY_CHART_SEEN_STORAGE_KEY, "true");
        setShowDailyNewBadge(false);
      }
    }
  };

  const processedData = useMemo(() => {
    if (!history.length) return { lineData: [], histogramData: [] };
    
    const prices = history.map(entry => ({
      time: new Date(entry.time + 'Z').getTime() / 1000 as UTCTimestamp,
      value: entry.price,
    }));

    const quantities = history.map(entry => ({
      time: new Date(entry.time + 'Z').getTime() / 1000 as UTCTimestamp,
      value: entry.quantity,
    }));

    return { lineData: prices, histogramData: quantities };
  }, [history]);

  const dailyChartData = useMemo<DailyStatsChartData>(() => {
    if (!dailyStats.length) return { candlestickData: [] };

    return {
      candlestickData: dailyStats.map((entry) => ({
        time: entry.time,
        open: entry.open,
        high: entry.high,
        low: entry.low,
        close: entry.close,
      })),
    };
  }, [dailyStats]);

  const isCurrentChartLoading = chartMode === "recent" ? isLoading : isDailyLoading;

  return (
    <DetailContainer>
      <HeaderContainer>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Button variant="outlined" onClick={onBack} disableRipple sx={{ userSelect: "none", "&:focus": { outline: "none" } }}>
            {language === "ko" ? translations["Back to List"] : "Back to List"}
          </Button>
          <ItemName
            iconUrl={item.iconUrl}
            name={"name" in item ? item.name : item.text}
            isUnique={"name" in item ? true : false}
            itemMetadata={item.itemMetadata}
          />
        </Box>
        <Box sx={{ display: "flex", flexDirection: "row", gap: 1 }}>
          <ToggleButtonGroup
            exclusive
            size="small"
            value={chartMode}
            onChange={handleChartModeChange}
          >
            <ToggleButton value="recent">Recent</ToggleButton>
            <ToggleButton
              value="daily"
              sx={
                showDailyNewBadge
                  ? {
                      "@keyframes dailyChartPulse": {
                        "0%": {
                          borderColor: "rgba(212, 175, 55, 0.55)",
                          boxShadow: "0 0 0 0 rgba(212, 175, 55, 0.45)",
                          color: "#f7d774",
                        },
                        "70%": {
                          borderColor: "rgba(247, 215, 116, 0.95)",
                          boxShadow: "0 0 0 8px rgba(212, 175, 55, 0)",
                          color: "#ffe08a",
                        },
                        "100%": {
                          borderColor: "rgba(212, 175, 55, 0.55)",
                          boxShadow: "0 0 0 0 rgba(212, 175, 55, 0)",
                          color: "#f7d774",
                        },
                      },
                      animation: "dailyChartPulse 1.8s ease-out infinite",
                    }
                  : undefined
              }
            >
              Daily
            </ToggleButton>
          </ToggleButtonGroup>
          {chartMode === "recent" && (
            <ReferenceCurrencySelector
              currentReference={selectedReference}
              onReferenceChange={onSelectedReferenceChange}
              options={referenceCurrencyOptions}
              currencyMeta={league}
            />
          )}
        </Box>
      </HeaderContainer>

      <Box sx={{ width: "100%", height: "500px", position: 'relative' }}>
        {isCurrentChartLoading ? (
          <Box sx={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <CircularProgress />
          </Box>
        ) : chartMode === "recent" ? (
          <div style={{ position: 'relative', width: '100%'}} >
            <ChartLegend
                {...legendData}
                selectedReference={selectedReference}
                selectedReferenceText={getCurrencyLabel(
                  selectedReference,
                  selectedReference === league.baseCurrencyApiId
                    ? league.baseCurrencyText
                    : undefined,
                  league,
                )}
            />
            <Chart
              chartData={processedData}
              onLoadMore={handleLoadMore}
              hasMore={hasMore}
              isLoadingMore={isLoadingMore}
              onLegendDataChange={setLegendData}
              height={500}
            />          
          </div>
        ) : (
          <div style={{ position: "relative", width: "100%" }}>
            <DailyStatsChartLegend
              {...dailyLegendData}
              baseCurrencyApiId={league.baseCurrencyApiId}
              baseCurrencyText={league.baseCurrencyText}
            />
            <DailyStatsChart
              chartData={dailyChartData}
              onLoadMore={handleDailyLoadMore}
              hasMore={dailyHasMore}
              isLoadingMore={isDailyLoadingMore}
              onLegendDataChange={setDailyLegendData}
              height={500}
            />
          </div>
        )}
      </Box>
    </DetailContainer>
  );
}
