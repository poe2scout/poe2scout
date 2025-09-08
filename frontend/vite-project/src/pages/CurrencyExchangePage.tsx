import { Box, CircularProgress, Alert, Paper, Typography, Stack } from "@mui/material";
import { useState, useEffect } from "react";
import { useLeague } from "../contexts/LeagueContext";
import SnapshotHeader from "../components/CurrencyExchange/SnapshotHeader";
import SnapshotHistory from "../components/CurrencyExchange/SnapshotHistory";

const uri = import.meta.env.VITE_API_URL;

export interface CurrencyExchangeSnapshot {
  Epoch: number;
  Volume: number;
  MarketCap: number;
}

const fetchCurrencyExchangeSnapshot = async (league: string) => {
  const response = await fetch(`${uri}/currencyExchangeSnapshot?league=${league}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch data: ${response.statusText}`);
  }
  return response.json();
};

export function CurrencyExchangePage() {
  const [snapshot, setSnapshot] = useState<CurrencyExchangeSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { league } = useLeague();

  useEffect(() => {
    const getStartingInfo = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const snapshotData = await fetchCurrencyExchangeSnapshot(league.value);
        setSnapshot({Epoch: snapshotData.Epoch, Volume: parseFloat(snapshotData.Volume), MarketCap: parseFloat(snapshotData.MarketCap)});
      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred.");
      } finally {
        setIsLoading(false);
      }
    };

    getStartingInfo();
  }, [league]);

  const renderContent = () => {
    if (isLoading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <CircularProgress />
        </Box>
      );
    }

    if (error) {
      return <Alert severity="error">{error}</Alert>;
    }

    if (snapshot) {
      return (
        <>
          <Box sx={{ p: 2 }}>
            <Stack spacing={2}>
              <SnapshotHeader snapshot={snapshot} />
              <SnapshotHistory snapshot={snapshot} />
            </Stack>
          </Box>
          <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
            <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6">Trading Pairs</Typography>
              <Typography variant="body2" color="text.secondary">
                Detailed pair information coming soon™
              </Typography>
            </Paper>
          </Box>
        </>
      );
    }
    return null;
  };

  return (
    <Box sx={{
      width: "100%",
      height: "calc(100vh - 64px)",
      display: "flex",
      flexDirection: "column",
    }}>
      {renderContent()}
    </Box>
  );
}

export default CurrencyExchangePage;