import { useEffect, useState, useMemo } from "react";
import {
  Button,
  ButtonGroup,
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
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

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
  const processedData = useMemo(() => {
    if (!detailedHistory.length) return { labels: [], prices: [] };

    // Reverse the array to get chronological order (oldest to newest)
    const firstValidIndexReverse = detailedHistory.findIndex(entry => entry !== null)

    const chronologicalHistory = [...(detailedHistory.slice(firstValidIndexReverse))].reverse();
    
    // Find the index of the first non-null entry
    const firstValidIndex = chronologicalHistory.findIndex(entry => entry !== null);
    
    // If no valid entries found, return empty arrays
    if (firstValidIndex === -1) return { labels: [], prices: [] };
    
    // Slice the array from the first valid entry
    const validHistory = chronologicalHistory.slice(firstValidIndex);
    
    let lastValidPrice = 0;
    const prices = validHistory.map((entry) => {
      if (!entry) {
        return lastValidPrice; // Use the last valid price for null entries
      }
      lastValidPrice = entry.price;
      return entry.price;
    });

    // Generate labels (dates) for the valid entries
    const labels = validHistory.map((entry) => 
      entry ? new Date(entry.time).toLocaleDateString() : ''
    );

    return { labels, prices };
  }, [detailedHistory]);

  const chartData = {
    labels: processedData.labels,
    datasets: [
      {
        label: 'Price History',
        data: processedData.prices,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        fill: false,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(tickValue: number | string) {
            return typeof tickValue === 'number' ? tickValue.toFixed(2) : tickValue;
          }
        }
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => `Price: ${context.parsed.y.toFixed(2)}`,
        },
      },
    },
  };

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
        <ButtonGroup>
          <Button
            variant={logCount === 28 ? "contained" : "outlined"}
            onClick={() => setLogCount(28)}
            disableRipple
            sx={{
              userSelect: "none",
              "&:focus": { outline: "none" },
            }}
          >
            {language === "ko" ? translations["Week"] : "Week"}
          </Button>
          <Button
            variant={logCount === 112 ? "contained" : "outlined"}
            onClick={() => setLogCount(112)}
            disableRipple
            sx={{
              userSelect: "none",
              "&:focus": { outline: "none" },
            }}
          >
            {language === "ko" ? translations["Month"] : "Month"}
          </Button>
          <Button
            variant={logCount === 336 ? "contained" : "outlined"}
            onClick={() => setLogCount(336)}
            disableRipple
            sx={{
              userSelect: "none",
              "&:focus": { outline: "none" },
            }}
          >
            {language === "ko" ? translations["3 Months"] : "3 Months"}
          </Button>
          <Button
            variant={logCount === 672 ? "contained" : "outlined"}
            onClick={() => setLogCount(672)}
            disableRipple
            sx={{
              userSelect: "none",
              "&:focus": { outline: "none" },
            }}
          >
            All
          </Button>
        </ButtonGroup>
      </HeaderContainer>

      <Box sx={{ height: 400, width: "100%" }}>
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
          <Line data={chartData} options={chartOptions} />
        )}
      </Box>
    </DetailContainer>
  );
}