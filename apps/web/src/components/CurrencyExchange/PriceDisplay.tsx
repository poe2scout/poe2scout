import { Box, Typography, TableCell } from "@mui/material";

import type { SnapshotPair } from "../../types";

interface PriceDisplayProps {
  isHovered: boolean;
  pair: SnapshotPair;
}

interface PriceDisplayProp {
  iconUrl: string;
  itemPrice: number;
}

function PriceDisplay({ iconUrl, itemPrice }: PriceDisplayProp) {
  return (
    <Box
      component="span"
      sx={{
        display: "inline-flex",
        alignItems: "center",
        fontWeight: "medium",
      }}
    >
      {itemPrice.toFixed(2)}
      <img
        style={{ width: "30px", marginLeft: "0.25em" }}
        src={iconUrl}
      />
    </Box>
  );
}

export function CurrencyExchangePriceDisplay({
  isHovered,
  pair,
}: PriceDisplayProps) {
  const item1Price = pair.currencyOneData.pairPrice || 0;
  const item2Price = pair.currencyTwoData.pairPrice || 0;

  return (
    <TableCell align="right" sx={{ py: 1 }}>
      <Typography variant="body2" noWrap component="div">
        {isHovered ? (
          <Box>
            <PriceDisplay
              iconUrl={pair.currencyTwo.iconUrl ?? ""}
              itemPrice={1.0}
            />{" "}
            ={" "}
            <PriceDisplay
              iconUrl={pair.currencyOne.iconUrl ?? ""}
              itemPrice={item2Price}
            />
          </Box>
        ) : (
          <>
            <PriceDisplay
              iconUrl={pair.currencyOne.iconUrl ?? ""}
              itemPrice={1.0}
            />{" "}
            ={" "}
            <PriceDisplay
              iconUrl={pair.currencyTwo.iconUrl ?? ""}
              itemPrice={item1Price}
            />
          </>
        )}
      </Typography>
    </TableCell>
  );
}
