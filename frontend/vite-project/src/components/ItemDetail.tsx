import { useEffect, useState, useMemo, useCallback } from "react";
import { Button, Paper, Box, CircularProgress } from "@mui/material";
import { styled } from "@mui/material/styles";
import { ItemName } from "./TableColumnComponents/ItemName";
import type { ApiItem } from "../types";
import { useLanguage } from "../contexts/LanguageContext";
import translations from "../translationskrmapping.json";
import { useLeague } from "../contexts/LeagueContext";
import { PriceLogEntry } from "../types";
import { Chart } from "./Chart";
import { UTCTimestamp } from "lightweight-charts";
import ReferenceCurrencySelector, { BaseCurrencies } from "./ReferenceCurrencySelector";

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
}

interface ApiHistoryResponse {
    price_history: PriceLogEntry[];
    has_more: boolean;
}

export function ItemDetail({ item, onBack }: ItemDetailProps) {
  const [logCount, setLogCount] = useState<number>(14*24); 
  const [history, setHistory] = useState<PriceLogEntry[]>([]);

  const [hasMore, setHasMore] = useState(true);
  const [oldestTimestamp, setOldestTimestamp] = useState<string>(() => new Date().toISOString());
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false); 

  const [selectedReference, setSelectedReference] = useState<BaseCurrencies>('exalted');
  const { language } = useLanguage();
  const { league } = useLeague();

  const fetchPriceHistory = useCallback(async (isInitialLoad: boolean, cursor: string) => {
    if (isInitialLoad) {
        setIsLoading(true);
    } else {
        setIsLoadingMore(true);
    }
    
    try {
      const url = `${import.meta.env.VITE_API_URL}/items/${item.itemId}/history?logCount=${logCount}&league=${league.value}&referenceCurrency=${selectedReference}&endTime=${cursor}`;
      console.log('Fetching URL:', url);
      
      const response = await fetch(url);
      const data: ApiHistoryResponse = await response.json();
      console.log('Fetched price history data:', data);

      setHistory(prevHistory => isInitialLoad ? data.price_history : [...data.price_history, ...prevHistory]);
      setHasMore(data.has_more);

      if (data.price_history.length > 0) {
        console.log("Setting oldest timestamp to " + data.price_history[0].time)
        setOldestTimestamp(data.price_history[0].time);
      }
    } catch (error) {
      console.error("Error fetching price history:", error);
      setHistory([]); // Reset on error
    } finally {
      if (isInitialLoad) setIsLoading(false);
      else setIsLoadingMore(false);
      setLogCount(prevLogCount => prevLogCount * 2)
    }
  }, [item.itemId, league.value, selectedReference]);

useEffect(() => {
    setHistory([]); 
    setHasMore(true);
    const initialCursor = new Date().toISOString();
    setOldestTimestamp(initialCursor);
    setLogCount(14 * 24); 

    fetchPriceHistory(true, initialCursor);
}, [item.id, selectedReference, fetchPriceHistory]);

  const handleLoadMore = useCallback(() => {
    if (!isLoadingMore && hasMore) {
        console.log(`handleLoadMore triggered, fetching older data...`+ oldestTimestamp);
        fetchPriceHistory(false, oldestTimestamp);
    }
  }, [isLoadingMore, hasMore, oldestTimestamp, fetchPriceHistory]);

  const onSelectedReferenceChange = (newReference: BaseCurrencies) => {
    setSelectedReference(newReference);
  };

  const processedData = useMemo(() => {
    if (!history.length) return { lineData: [], histogramData: [] };
    
    const prices = history.map(entry => ({
      time: new Date(entry.time).getTime() / 1000 as UTCTimestamp,
      value: entry.price,
    }));

    const quantities = history.map(entry => ({
      time: new Date(entry.time).getTime() / 1000 as UTCTimestamp,
      value: entry.quantity,
    }));

    return { lineData: prices, histogramData: quantities };
  }, [history]);

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
        <Box sx={{ display: 'flex', flexDirection: 'row' }}>
          <ReferenceCurrencySelector
            currentReference={selectedReference}
            onReferenceChange={onSelectedReferenceChange}
          />
        </Box>
      </HeaderContainer>

      <Box sx={{ width: "100%", height: "500px", position: 'relative' }}>
        {isLoading ? (
          <Box sx={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <CircularProgress />
          </Box>
        ) : (
          <Chart
            lineData={processedData.lineData}
            histogramData={processedData.histogramData}
            selectedReference={selectedReference}
            onLoadMore={handleLoadMore}
            hasMore={hasMore}
            isLoadingMore={isLoadingMore}
          />
        )}
      </Box>
    </DetailContainer>
  );
}
