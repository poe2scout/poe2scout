import { Paper, Stack, Typography } from "@mui/material";

import { ItemName } from "../../TableColumnComponents/ItemName";
import { FormatTimeFromEpoch } from "../../FormatTime";
import type { PairHistoryEntry, SnapshotPair } from "../api";

interface PairHistoryHeaderProps {
  pair: SnapshotPair | null;
  currencyOneItemId: number;
  currencyTwoItemId: number;
  latestEntry?: PairHistoryEntry;
}

export const PairHistoryHeader = ({
  pair,
  currencyOneItemId,
  currencyTwoItemId,
  latestEntry,
}: PairHistoryHeaderProps) => {
  const baseLabel = pair?.CurrencyOne.text ?? `Item ${currencyOneItemId}`;
  const quoteLabel = pair?.CurrencyTwo.text ?? `Item ${currencyTwoItemId}`;

  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Stack spacing={2}>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          justifyContent="space-between"
          alignItems={{ xs: "flex-start", sm: "center" }}
          spacing={1}
        >
          {pair ? (
            <Stack direction="row" spacing={1} alignItems="center">
              <ItemName
                iconUrl={pair.CurrencyOne.iconUrl}
                name={pair.CurrencyOne.text}
                isUnique={false}
                itemMetadata={pair.CurrencyOne.itemMetadata}
              />
              <Typography variant="body2" color="text.secondary" sx={{ px: 0.5 }}>
                /
              </Typography>
              <ItemName
                iconUrl={pair.CurrencyTwo.iconUrl}
                name={pair.CurrencyTwo.text}
                isUnique={false}
                itemMetadata={pair.CurrencyTwo.itemMetadata}
                iconPostFixed
              />
            </Stack>
          ) : (
            <Typography variant="h5">
              Pair {currencyOneItemId} / {currencyTwoItemId}
            </Typography>
          )}
          {latestEntry && (
            <Typography variant="body2" color="text.secondary">
              Updated {FormatTimeFromEpoch(latestEntry.Epoch)}
            </Typography>
          )}
        </Stack>

        {latestEntry && (
          <Stack
            direction={{ xs: "column", md: "row" }}
            spacing={2}
            justifyContent="space-between"
          >
            <Stack spacing={0.5}>
              <Typography variant="subtitle2">{quoteLabel}</Typography>
              <Typography variant="body2">
                Volume traded: {latestEntry.Data.CurrencyTwoData.VolumeTraded.toLocaleString()}
              </Typography>
              <Typography variant="body2">
                Value traded: {latestEntry.Data.CurrencyTwoData.ValueTraded.toLocaleString()}
              </Typography>
              <Typography variant="body2">
                Stock: {latestEntry.Data.CurrencyTwoData.HighestStock.toLocaleString()}
              </Typography>
            </Stack>
            <Stack spacing={0.5}>
              <Typography variant="subtitle2">{baseLabel}</Typography>
              <Typography variant="body2">
                Volume traded: {latestEntry.Data.CurrencyOneData.VolumeTraded.toLocaleString()}
              </Typography>
              <Typography variant="body2">
                Value traded: {latestEntry.Data.CurrencyOneData.ValueTraded.toLocaleString()}
              </Typography>
              <Typography variant="body2">
                Stock: {latestEntry.Data.CurrencyOneData.HighestStock.toLocaleString()}
              </Typography>
            </Stack>
          </Stack>
        )}
      </Stack>
    </Paper>
  );
};

export default PairHistoryHeader;
