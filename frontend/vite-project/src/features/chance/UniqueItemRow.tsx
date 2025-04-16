import { Grid2 as Grid, Chip, Tooltip } from "@mui/material";
import { PriceDisplay } from "../../components/TableColumnComponents/PriceDisplay";
import { ItemName } from "../../components/TableColumnComponents/ItemName";
import { PriceHistory } from "../../components/TableColumnComponents/PriceHistory";
import { UniqueItemExtended } from "../../types";
import { League } from "../../contexts/LeagueContext";
import BlockIcon from '@mui/icons-material/Block';

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
        opacity: item.isChanceable ? 1 : 0.7,
        '&:last-child': { borderBottom: 0 }
      }}
    >
      <Grid container size={{xs: 6}} sx={{ display: 'block', alignItems: 'center', gap: 1 }}>
        <ItemName
          iconUrl={item.iconUrl}
          name={item.name}
          isUnique={true}
          itemMetadata={item.itemMetadata}
        />
        {!item.isChanceable && (
          <Tooltip title="This item cannot be obtained through Chance Orbs">
            <Chip
              icon={<BlockIcon />}
              label="Not Chanceable"
              size="small"
              color="warning"
              sx={{ ml: 1 }}
            />
          </Tooltip>
        )}
      </Grid>
      <Grid size={{xs: 3}} sx={{ textAlign: "right" }}>
        <PriceDisplay
          currentPrice={item.currentPrice}
          divinePrice={league.divinePrice}
        />
      </Grid>
      <Grid
        size={{xs: 3}}
        sx={{ 
          textAlign: "right",
          display: 'flex',
          justifyContent: 'flex-end',
          minWidth: 0,
          overflow: 'hidden'
        }}
      >
        <PriceHistory priceHistory={item.priceLogs} variant="compact" />
      </Grid>
    </Grid>
  );
} 