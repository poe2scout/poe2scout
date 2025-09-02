import { useEffect, useState, useMemo } from "react";
import {
  Button,
  Paper,
  Box,
  CircularProgress,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import { ItemName } from "./TableColumnComponents/ItemName";
import type { ApiItem } from "../types";
import { useLanguage } from "../contexts/LanguageContext";
import translations from "../translationskrmapping.json";
import { useLeague } from "../contexts/LeagueContext";
import { PriceLogEntry } from "../types";
import { Chart } from "./Chart";
import { HistogramData, LineData, Time, UTCTimestamp } from "lightweight-charts";
import PeriodSelector from "./PeriodSelector";

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

interface ChartData {
  lineData: LineData<Time>[];
  histogramData: HistogramData<Time>[];
}

export function ItemDetail({ item, onBack }: ItemDetailProps) {
  console.log('ItemDetail render - props:', { item });
  const [logCount, setLogCount] = useState<number>(28);
  const [detailedHistory, setDetailedHistory] = useState<(PriceLogEntry | null)[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { language } = useLanguage();
  const { league } = useLeague();

  useEffect(() => {
    const fetchPriceHistory = async () => {
      console.log('Fetching price history:', { itemId: item.id, logCount, league });
      setIsLoading(true);
      try {
        const url = `${import.meta.env.VITE_API_URL}/items/${item.itemId}/history?logCount=${logCount}&league=${league.value}`;
        console.log('Fetch URL:', url);
        
        const response = await fetch(url);
        const data = await response.json();
        console.log('Fetched price history data:', data);
        setDetailedHistory(data.price_history);
      } catch (error) {
        console.error("Error fetching price history:", error);
        setDetailedHistory([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPriceHistory();
  }, [item.id, logCount]);

  // Process the price history data
  const processedData = useMemo((): ChartData => {
    if (!detailedHistory.length) return {lineData: [], histogramData: []};

    // Reverse the array to get chronological order (oldest to newest)
    const firstValidIndexReverse = detailedHistory.findIndex(entry => entry !== null)

    const chronologicalHistory = [...(detailedHistory.slice(firstValidIndexReverse))].reverse();
    
    // Find the index of the first non-null entry
    const firstValidIndex = chronologicalHistory.findIndex(entry => entry !== null);
    
    // If no valid entries found, return empty arrays
    if (firstValidIndex === -1) return {lineData: [], histogramData: []};
    
    // Slice the array from the first valid entry
    const validHistory = chronologicalHistory.slice(firstValidIndex);
    
    const prices = validHistory
      .filter(entry => entry && entry.time && typeof entry.price === 'number')
      .map(entry => {
        return {
          time: new Date(entry!.time).getTime() / 1000 as UTCTimestamp,
          value: entry!.price,
        };
      });

    const quantities = validHistory
      .filter(entry => entry && entry.time && typeof entry.price === 'number')
      .map(entry => {
        return {
          time: new Date(entry!.time).getTime() / 1000 as UTCTimestamp,
          value: entry!.quantity,
        };
      });

    return {
      lineData: prices,
      histogramData: quantities
    };
  }, [detailedHistory]);

  return (
    <DetailContainer>
      <HeaderContainer>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Button
            variant="outlined"
            onClick={onBack}
            disableRipple
            sx={{
              userSelect: "none",
              "&:focus": {
                outline: "none",
              },
            }}
          >
            {language === "ko" ? translations["Back to List"] : "Back to List"}
          </Button>
          <ItemName
            iconUrl={item.iconUrl}
            name={"name" in item ? item.name : item.text}
            isUnique={"name" in item ? true : false}
            itemMetadata={item.itemMetadata}
          />
        </Box>
        <PeriodSelector
          currentLogCount={logCount}
          onLogCountChange={setLogCount}
          language={language}
          translations={translations}
        />
      </HeaderContainer>

      <Box sx={{ width: "100%", height: "100%" }}>
        {isLoading ? (
          <Box
            sx={{
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <CircularProgress />
          </Box>
        ) : (
          <Chart lineData={processedData.lineData} histogramData={processedData.histogramData} />
        )}
      </Box>
    </DetailContainer>
  );
}