import { Grid2 as Grid, Typography } from "@mui/material";
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
      <Grid
        container
        sx={{
          p: { xs: 0.5, sm: 1 },
          bgcolor: 'background.paper',
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
        }}
      >
        <Grid size={{xs: 12, sm: 6}} sx={{ mb: { xs: 0.5, sm: 0 } }}>
          <Typography variant="subtitle2" color="text.secondary" sx={{ fontSize: { xs: '0.75rem', sm: 'inherit' } }}>
            Name
          </Typography>
        </Grid>
        <Grid size={{xs: 6, sm: 3}} >
          <Typography variant="subtitle2" color="text.secondary" sx={{ fontSize: { xs: '0.75rem', sm: 'inherit' } }}>
            Price
          </Typography>
        </Grid>
        <Grid size={{xs: 6, sm: 3}} >
          <Typography variant="subtitle2" color="text.secondary" sx={{ fontSize: { xs: '0.75rem', sm: 'inherit' } }}>
            Trend
          </Typography>
        </Grid>
      </Grid>

      {items.map((item) => (
        <UniqueItemRow key={item.itemId} item={item} league={league} />
      ))}
    </>
  );
} 