import { Alert, Box, Button, CircularProgress, Stack } from "@mui/material";
import type { SelectChangeEvent } from "@mui/material/Select";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { UTCTimestamp } from "lightweight-charts";

import type { ChartData } from "../components/Chart";
import PairHistoryChartSection from "../components/CurrencyExchange/PairHistory/PairHistoryChartSection";
import PairHistoryHeader from "../components/CurrencyExchange/PairHistory/PairHistoryHeader";
import {
  fetchPairHistory,
  fetchSnapshotPairs,
  normalizePairHistoryResponse,
  PairHistoryEntry,
  SnapshotPair,
} from "../components/CurrencyExchange/api";
import { useLeague } from "../contexts/LeagueContext";
import {
  DataKey,
  MetricKey,
  MetricMenuOption,
  MetricOption,
} from "../components/CurrencyExchange/PairHistory/metricTypes";
import { METRIC_BASE_LABELS } from "../components/CurrencyExchange/PairHistory/metricLabels";

const HISTORY_LIMIT = 24 * 14;
const DEFAULT_METRIC_ID = "CurrencyTwoData.ValueTraded";

const findPairByItems = (
  pairs: SnapshotPair[],
  currencyOneItemId: number,
  currencyTwoItemId: number,
) =>
  pairs.find((candidate) => {
    const candidateIds = [
      candidate.CurrencyOne.itemId,
      candidate.CurrencyTwo.itemId,
    ];
    return (
      candidateIds.includes(currencyOneItemId) &&
      candidateIds.includes(currencyTwoItemId)
    );
  }) ?? null;

const getLineUnit = (option: MetricOption | null): string => {
  if (!option) {
    return "";
  }

  switch (option.metricKey) {
    case "ValueTraded":
    case "StockValue":
      return "Exalted Orbs";
    case "VolumeTraded":
    case "HighestStock":
      return option.itemName;
    case "PairPrice":
    default:
      return option.counterpartName;
  }
};

export function PairHistoryPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const locationState = location.state as { pair?: SnapshotPair } | undefined;
  const { league } = useLeague();
  const params = useParams();

  const currencyOneItemId = Number(params.currencyOneItemId);
  const currencyTwoItemId = Number(params.currencyTwoItemId);
  const hasInvalidIds =
    Number.isNaN(currencyOneItemId) || Number.isNaN(currencyTwoItemId);

  const [pair, setPair] = useState<SnapshotPair | null>(
    locationState?.pair ?? null,
  );
  const [isPairLoading, setIsPairLoading] = useState(!locationState?.pair);
  const [pairError, setPairError] = useState<string | null>(null);

  const [history, setHistory] = useState<PairHistoryEntry[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [oldestEpoch, setOldestEpoch] = useState<number | null>(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  const [selectedMetricId, setSelectedMetricId] = useState(DEFAULT_METRIC_ID);

  useEffect(() => {
    if (locationState?.pair) {
      setPair(locationState.pair);
      setIsPairLoading(false);
      setPairError(null);
    }
  }, [locationState]);

  useEffect(() => {
    if (pair) {
      return;
    }

    let isActive = true;

    const loadPairDetails = async () => {
      try {
        setIsPairLoading(true);
        setPairError(null);
        const snapshotPairs = await fetchSnapshotPairs(league);

        if (!isActive) {
          return;
        }

        const matchedPair = findPairByItems(
          snapshotPairs,
          currencyOneItemId,
          currencyTwoItemId,
        );

        if (matchedPair) {
          setPair(matchedPair);
        } else {
          setPairError(
            "Pair is not present in the current snapshot. Showing history only.",
          );
        }
      } catch (err) {
        if (isActive) {
          const message =
            err instanceof Error
              ? err.message
              : "Failed to load snapshot pair details.";
          setPairError(message);
        }
      } finally {
        if (isActive) {
          setIsPairLoading(false);
        }
      }
    };

    loadPairDetails();

    return () => {
      isActive = false;
    };
  }, [pair, league, currencyOneItemId, currencyTwoItemId]);

  useEffect(() => {
    let isMounted = true;

    const loadHistory = async () => {
      if (hasInvalidIds) {
        setHistoryError("The selected pair is not valid.");
        setIsHistoryLoading(false);
        return;
      }

      try {
        setIsHistoryLoading(true);
        setHistoryError(null);
        const dto = await fetchPairHistory({
          league: league.value,
          currencyOneItemId,
          currencyTwoItemId,
          limit: HISTORY_LIMIT,
        });

        if (!isMounted) {
          return;
        }

        const { history: fetchedHistory, hasMore: fetchedHasMore } =
          normalizePairHistoryResponse(dto);
        const orderedHistory = [...fetchedHistory].sort(
          (a, b) => a.Epoch - b.Epoch,
        );

        setHistory(orderedHistory);
        setHasMore(fetchedHasMore);
        setOldestEpoch(orderedHistory[0]?.Epoch ?? null);
      } catch (err) {
        if (isMounted) {
          const message =
            err instanceof Error
              ? err.message
              : "Failed to fetch pair history.";
          setHistoryError(message);
          setHistory([]);
          setHasMore(false);
          setOldestEpoch(null);
        }
      } finally {
        if (isMounted) {
          setIsHistoryLoading(false);
        }
      }
    };

    loadHistory();

    return () => {
      isMounted = false;
    };
  }, [
    league.value,
    currencyOneItemId,
    currencyTwoItemId,
    hasInvalidIds,
  ]);

  const handleLoadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore || !oldestEpoch) {
      return;
    }

    setIsLoadingMore(true);
    try {
      const dto = await fetchPairHistory({
        league: league.value,
        currencyOneItemId,
        currencyTwoItemId,
        limit: HISTORY_LIMIT,
        endEpoch: oldestEpoch,
      });

      const { history: fetchedHistory, hasMore: fetchedHasMore } =
        normalizePairHistoryResponse(dto);
      const orderedHistory = [...fetchedHistory].sort(
        (a, b) => a.Epoch - b.Epoch,
      );

      if (orderedHistory.length === 0) {
        setHasMore(fetchedHasMore);
        return;
      }

      setHistory((prev) => [...orderedHistory, ...prev]);
      setHasMore(fetchedHasMore);
      setOldestEpoch(orderedHistory[0].Epoch);
    } catch (err) {
      console.error("Failed to load more pair history", err);
    } finally {
      setIsLoadingMore(false);
    }
  }, [
    currencyOneItemId,
    currencyTwoItemId,
    league.value,
    hasMore,
    oldestEpoch,
    isLoadingMore,
  ]);

  const metricOptions = useMemo<MetricOption[]>(() => {
    const defaultNames = {
      CurrencyOneData: `Item ${currencyOneItemId}`,
      CurrencyTwoData: `Item ${currencyTwoItemId}`,
    } as const;

    const dataSources: Array<{ key: DataKey; name: string }> = [
      {
        key: "CurrencyTwoData",
        name: pair?.CurrencyTwo.text ?? defaultNames.CurrencyTwoData,
      },
      {
        key: "CurrencyOneData",
        name: pair?.CurrencyOne.text ?? defaultNames.CurrencyOneData,
      },
    ];

    const getCounterpartName = (key: DataKey) =>
      key === "CurrencyTwoData"
        ? pair?.CurrencyOne.text ?? defaultNames.CurrencyOneData
        : pair?.CurrencyTwo.text ?? defaultNames.CurrencyTwoData;

    const metricsOrder: MetricKey[] = [
      "PairPrice",
      "ValueTraded",
      "VolumeTraded",
      "StockValue",
      "HighestStock",
    ];

    return dataSources.flatMap((source) => {
      const itemName = source.name;
      const counterpartName = getCounterpartName(source.key);

      return metricsOrder.map((metric) => ({
        id: `${source.key}.${metric}`,
        dataKey: source.key,
        metricKey: metric,
        menuLabel: `${METRIC_BASE_LABELS[metric]} (${itemName})`,
        itemName,
        counterpartName,
      }));
    });
  }, [pair, currencyOneItemId, currencyTwoItemId]);

  useEffect(() => {
    if (metricOptions.length === 0) {
      return;
    }

    const isSelectedValid = metricOptions.some(
      (option) => option.id === selectedMetricId,
    );

    if (!isSelectedValid) {
      setSelectedMetricId(metricOptions[0].id);
    }
  }, [metricOptions, selectedMetricId]);

  const selectedOption = useMemo(
    () =>
      metricOptions.find((option) => option.id === selectedMetricId) ??
      metricOptions[0] ?? null,
    [metricOptions, selectedMetricId],
  );

  const metricMenuOptions = useMemo<MetricMenuOption[]>(
    () => metricOptions.map(({ id, menuLabel }) => ({ id, menuLabel })),
    [metricOptions],
  );

  const chartData = useMemo<ChartData>(() => {
    if (!selectedOption) {
      return { lineData: [], histogramData: [] };
    }

    const lineData = history
      .map((entry) => {
        const value =
          entry.Data[selectedOption.dataKey][selectedOption.metricKey];
        if (!Number.isFinite(value)) {
          return null;
        }
        return {
          time: entry.Epoch as UTCTimestamp,
          value,
        };
      })
      .filter((entry): entry is { time: UTCTimestamp; value: number } =>
        entry !== null,
      );

    const histogramData = history.map((entry) => ({
      time: entry.Epoch as UTCTimestamp,
      value: entry.Data[selectedOption.dataKey].VolumeTraded,
    }));

    return { lineData, histogramData };
  }, [history, selectedOption]);

  const handleMetricChange = (event: SelectChangeEvent) => {
    setSelectedMetricId(event.target.value as string);
  };

  const latestEntry = history[history.length - 1];
  const quoteLabel = pair?.CurrencyTwo.text ?? `Item ${currencyTwoItemId}`;

  const lineUnit = getLineUnit(selectedOption);
  const legendLineLabel = selectedOption
    ? `${METRIC_BASE_LABELS[selectedOption.metricKey]}${lineUnit ? ` (${lineUnit})` : ""}`
    : "Metric";

  const histogramUnit = selectedOption?.itemName ?? quoteLabel;
  const legendHistogramLabel = `Volume traded (${histogramUnit})`;

  const chartMetricKey: MetricKey = selectedOption?.metricKey ?? "ValueTraded";

  const backToExchange = () => navigate("/exchange");

  if (isHistoryLoading) {
    return (
      <Box
        sx={{
          width: "100%",
          height: "calc(100vh - 64px)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (historyError) {
    return (
      <Box
        sx={{
          width: "100%",
          height: "calc(100vh - 64px)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Alert severity="error">{historyError}</Alert>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        width: "100%",
        height: "calc(100vh - 64px)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box sx={{ p: 2, pb: 0 }}>
        <Button variant="text" onClick={backToExchange}>
          Back to snapshot
        </Button>
      </Box>
      <Box sx={{ flexGrow: 1, p: 2, pt: 1, overflowY: "auto" }}>
        <Stack spacing={2}>
          {pairError && !isPairLoading && (
            <Alert severity="warning">{pairError}</Alert>
          )}
          <PairHistoryHeader
            pair={pair}
            currencyOneItemId={currencyOneItemId}
            currencyTwoItemId={currencyTwoItemId}
            latestEntry={latestEntry}
          />
          <PairHistoryChartSection
            chartData={chartData}
            hasMore={hasMore}
            isLoadingMore={isLoadingMore}
            onLoadMore={handleLoadMore}
            metricOptions={metricMenuOptions}
            selectedMetricId={selectedOption?.id ?? ""}
            onMetricChange={handleMetricChange}
            selectedMetricKey={chartMetricKey}
            legendLineLabel={legendLineLabel}
            legendHistogramLabel={legendHistogramLabel}
          />
        </Stack>
      </Box>
    </Box>
  );
}

export default PairHistoryPage;
