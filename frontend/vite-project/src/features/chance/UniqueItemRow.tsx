import { Grid } from "@mui/material";
import { PriceDisplay } from "../../components/TableColumnComponents/PriceDisplay";
import { ItemName } from "../../components/TableColumnComponents/ItemName";
import { PriceHistory } from "../../components/TableColumnComponents/PriceHistory";
import { UniqueItemExtended } from "../../types";
import { League } from "../../contexts/LeagueContext";

interface UniqueItemRowProps {
  item: UniqueItemExtended;
  league: League;
}

export function UniqueItemRow({ item, league }: UniqueItemRowProps) {
  return (
    <Grid
      container
      alignItems="center"
      sx={{
        p: 1,
        '&:hover': { bgcolor: 'action.hover' },
        borderBottom: 1,
        borderColor: 'divider',
        '&:last-child': { borderBottom: 0 }
      }}
    >
      {/* Name & Base Type using ItemName component */}
      <Grid item xs={6}>
        <ItemName
          iconUrl={item.iconUrl}
          name={item.name}
          isUnique={true}
          itemMetadata={item.itemMetadata}
        />
      </Grid>

      {/* Price using PriceDisplay component */}
      <Grid item xs={3} sx={{ textAlign: "right" }}>
        <PriceDisplay
          currentPrice={item.currentPrice}
          divinePrice={league.divinePrice}
        />
      </Grid>

      {/* Trend using PriceHistory component */}
      <Grid item xs={3} sx={{ textAlign: "right" }}>
        <PriceHistory priceHistory={item.priceLogs} />
      </Grid>
    </Grid>
  );
} 