import { useState } from "react";
import { SnapshotPair } from "./SnapshotPairList";
import { Stack, styled, TableCell, TableRow, Typography } from "@mui/material";
import { ItemName } from "../TableColumnComponents/ItemName";
import { CurrencyExchangePriceDisplay } from "./PriceDisplay";

const ClickableTableRow = styled(TableRow)(({ theme }) => ({
  "&:hover": {
    backgroundColor: theme.palette.action.hover,
  },
  cursor: "pointer"
}));


export const SnapshotPairRow = (params: {pair: SnapshotPair, onPairClick: (pair: SnapshotPair) => void} ) => {
  const [isHovered, setIsHovered] = useState(false);

  const pair = params.pair
  const onPairClick = params.onPairClick

  return (
    <ClickableTableRow
      onClick={() => onPairClick(pair)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <TableCell component="th" scope="row" sx={{ py: 1 }}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <ItemName iconUrl={pair.CurrencyOne.iconUrl} name={pair.CurrencyOne.text} isUnique={false} itemMetadata={pair.CurrencyOne.itemMetadata} />
          <Typography variant="body2" color="text.secondary">/ </Typography>
          <ItemName iconUrl={pair.CurrencyTwo.iconUrl} name={pair.CurrencyTwo.text} isUnique={false} itemMetadata={pair.CurrencyTwo.itemMetadata} iconPostFixed={true} />
        </Stack>
      </TableCell>

      <CurrencyExchangePriceDisplay pair={pair} isHovered={isHovered} />

      <TableCell align="right" sx={{ py: 1 }}>
        <Typography variant="body2">{pair.Volume.toLocaleString(undefined, { maximumFractionDigits: 0 })}</Typography>
      </TableCell>
    </ClickableTableRow>
  );
};
