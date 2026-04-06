import { Paper, Stack, Typography } from "@mui/material";

import type { PairHistoryEntry, SnapshotPair } from "../../../types";
import { FormatTimeFromEpoch } from "../../FormatTime";
import { ItemName } from "../../TableColumnComponents/ItemName";

interface PairHistoryHeaderProps {
  pair: SnapshotPair | null;
  currencyOneItemId: number;
  currencyTwoItemId: number;
  latestEntry?: PairHistoryEntry;
  baseCurrencyText: string;
}

export const PairHistoryHeader = ({
  pair,
  currencyOneItemId,
  currencyTwoItemId,
  latestEntry,
  baseCurrencyText,
}: PairHistoryHeaderProps) => {
  const baseLabel = pair?.currencyOne.text ?? `Item ${currencyOneItemId}`;
  const quoteLabel = pair?.currencyTwo.text ?? `Item ${currencyTwoItemId}`;

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
                iconUrl={pair.currencyOne.iconUrl}
                name={pair.currencyOne.text}
                isUnique={false}
                itemMetadata={pair.currencyOne.itemMetadata}
              />
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ px: 0.5 }}
              >
                /
              </Typography>
              <ItemName
                iconUrl={pair.currencyTwo.iconUrl}
                name={pair.currencyTwo.text}
                isUnique={false}
                itemMetadata={pair.currencyTwo.itemMetadata}
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
              Updated {FormatTimeFromEpoch(latestEntry.epoch)}
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
                Volume traded:{" "}
                {latestEntry.data.currencyTwoData.volumeTraded.toLocaleString()}
              </Typography>
              <Typography variant="body2">
                Value traded:{" "}
                {latestEntry.data.currencyTwoData.valueTraded.toLocaleString()}{" "}
                {baseCurrencyText}
              </Typography>
              <Typography variant="body2">
                Stock:{" "}
                {latestEntry.data.currencyTwoData.highestStock.toLocaleString()}
              </Typography>
            </Stack>
            <Stack spacing={0.5}>
              <Typography variant="subtitle2">{baseLabel}</Typography>
              <Typography variant="body2">
                Volume traded:{" "}
                {latestEntry.data.currencyOneData.volumeTraded.toLocaleString()}
              </Typography>
              <Typography variant="body2">
                Value traded:{" "}
                {latestEntry.data.currencyOneData.valueTraded.toLocaleString()}{" "}
                {baseCurrencyText}
              </Typography>
              <Typography variant="body2">
                Stock:{" "}
                {latestEntry.data.currencyOneData.highestStock.toLocaleString()}
              </Typography>
            </Stack>
          </Stack>
        )}
      </Stack>
    </Paper>
  );
};

export default PairHistoryHeader;
