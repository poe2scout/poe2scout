import { Box, CircularProgress, Alert, Stack } from "@mui/material";
import { useState, useEffect } from "react";

import SnapshotHeader from "../components/CurrencyExchange/SnapshotHeader";
import SnapshotHistory from "../components/CurrencyExchange/SnapshotHistory";
import SnapshotPairList from "../components/CurrencyExchange/SnapshotPairList";
import { fetchCurrentSnapshot } from "../components/CurrencyExchange/api";
import { useLeague } from "../contexts/LeagueContext";
import type { CurrencyExchangeSnapshot } from "../types";

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
        const snapshotData = await fetchCurrentSnapshot(league.value);
        setSnapshot(snapshotData);
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
      );
    }

    if (error) {
      return <Alert severity="error">{error}</Alert>;
    }

    if (snapshot) {
      return (
        <Box sx={{ flexGrow: 1, p: 2, overflowY: "auto" }}>
          <Box sx={{ p: 2 }}>
            <Stack spacing={2}>
              <SnapshotHeader snapshot={snapshot} />
              <SnapshotHistory snapshot={snapshot} />
            </Stack>
          </Box>
          <Box sx={{ flexGrow: 1, p: 2, overflowY: "auto" }}>
            <SnapshotPairList snapshot={snapshot} />
          </Box>
        </Box>
      );
    }

    return null;
  };

  return (
    <Box
      sx={{
        width: "100%",
        height: "calc(100vh - 64px)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {renderContent()}
    </Box>
  );
}

export default CurrencyExchangePage;
