import { Grid, Typography } from "@mui/material";
import { UniqueItemRow } from "./UniqueItemRow";
import { UniqueItemExtended } from "../../types";
import { League } from "../../contexts/LeagueContext";

interface UniqueItemsGridProps {
  items: UniqueItemExtended[];
  league: League;
}

export function UniqueItemsGrid({ items, league }: UniqueItemsGridProps) {
  return (
    <>
      {/* Header */}
      <Grid
        container
        sx={{
          p: 1,
          bgcolor: 'background.paper',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Grid item xs={6}>
          <Typography variant="subtitle2" color="text.secondary">
            Name
          </Typography>
        </Grid>
        <Grid item xs={3} sx={{ textAlign: "right" }}>
          <Typography variant="subtitle2" color="text.secondary">
            Price
          </Typography>
        </Grid>
        <Grid item xs={3} sx={{ textAlign: "right" }}>
          <Typography variant="subtitle2" color="text.secondary">
            Trend
          </Typography>
        </Grid>
      </Grid>

      {/* Items */}
      {items.map((item) => (
        <UniqueItemRow key={item.itemId} item={item} league={league} />
      ))}
    </>
  );
} 