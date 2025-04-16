import { Card, Box, Typography, Avatar, CardContent, Chip } from "@mui/material";
import { League } from "../../contexts/LeagueContext"; // Import League type
import { PriceDisplay } from "../../components/TableColumnComponents/PriceDisplay";
import { UniqueBaseItem } from "../../types";
import BlockIcon from '@mui/icons-material/Block';

interface BaseItemCardProps {
  item: UniqueBaseItem;
  isSelected: boolean;
  onClick: () => void;
  league: League; // Pass league for divinePrice
}

export function BaseItemCard({ item, isSelected, onClick, league }: BaseItemCardProps) {
  const basePriceTrendColor = item.currentPrice === null ? "text.secondary" :
                             item.currentPrice > 0 ? "success.main" : "error.main";
  const lastBasePrice = item.priceLogs[item.priceLogs.length - 1]?.price;
  const basePriceChange = item.currentPrice !== null && lastBasePrice !== undefined ? item.currentPrice - lastBasePrice : 0;

  return (  
    <Card
      variant="outlined"
      sx={{
        cursor: 'pointer',
        bgcolor: isSelected ? "action.selected" : "background.paper",
        borderColor: isSelected ? "primary.main" : "divider",
        opacity: item.isChanceable ? 1 : 0.7,
        '&:hover': {
          bgcolor: isSelected ? 'action.selected' : 'action.hover',
        },
      }}
      onClick={onClick}
    >
      <CardContent sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1,
        py: '8px !important'
      }}>
        <Avatar
          src={item.iconUrl || "/img/placeholder-icon.png"}
          alt={item.name}
          variant="square"
          sx={{ width: 40, height: 40 }}
        />
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          <Typography variant="body1" fontWeight="medium" noWrap>
            {item.name}
          </Typography>
        </Box>
        {!item.isChanceable && (
          <Chip
            icon={<BlockIcon />}
            label="Not Chanceable"
            size="small"
            color="warning"
            sx={{ ml: 1 }}
          />
        )}
        <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Base: <PriceDisplay currentPrice={item.currentPrice} divinePrice={league.divinePrice} />
              {item.currentPrice !== null && lastBasePrice !== undefined && (
                <Typography component="span" variant="caption" color={basePriceTrendColor} sx={{ ml: 0.5 }}>
                  {basePriceChange > 0 ? "+" : ""}{basePriceChange.toFixed(1)}%
                </Typography>
              )}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ marginLeft: 3 }}>
              Avg. Unique: <PriceDisplay currentPrice={item.averageUniquePrice} divinePrice={league.divinePrice} />
            </Typography>

          </Box>
      </CardContent>
    </Card>
  );
} 