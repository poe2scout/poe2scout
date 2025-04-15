import { Card, Box, Typography, Avatar, CardContent } from "@mui/material";
import { League } from "../../contexts/LeagueContext"; // Import League type
import { PriceDisplay } from "../../components/TableColumnComponents/PriceDisplay";
import { UniqueBaseItem } from "../../types";

interface BaseItemCardProps {
  item: UniqueBaseItem;
  isSelected: boolean;
  onClick: () => void;
  league: League; // Pass league for divinePrice
}

export function BaseItemCard({ item, isSelected, onClick, league }: BaseItemCardProps) {
  const uniquePriceTrendColor = item.averageUniquePrice === null ? "text.secondary" :
                               item.averageUniquePrice > 0 ? "success.main" : "error.main";
  const basePriceTrendColor = item.currentPrice === null ? "text.secondary" :
                             item.currentPrice > 0 ? "success.main" : "error.main";

  return (
    <Card
      variant="outlined"
      sx={{
        cursor: 'pointer',
        bgcolor: isSelected ? "action.selected" : "background.paper",
        borderColor: isSelected ? "primary.main" : "divider",
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
          <Typography variant="body2" color="text.secondary" noWrap>
            iLvl: {item.itemMetadata?.requirements["level"]}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Base: <PriceDisplay currentPrice={item.currentPrice} divinePrice={league.divinePrice} />
              {item.currentPrice !== null && (
                <Typography component="span" variant="caption" color={basePriceTrendColor} sx={{ ml: 0.5 }}>
                  {item.currentPrice > 0 ? "+" : ""}{item.currentPrice.toFixed(1)}%
                </Typography>
              )}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ marginLeft: 3 }}>
              Avg. Unique: <PriceDisplay currentPrice={item.averageUniquePrice} divinePrice={league.divinePrice} />
              {item.averageUniquePrice !== null && (
                <Typography component="span" variant="caption" color={uniquePriceTrendColor} sx={{ ml: 0.5 }}>
                  {item.averageUniquePrice > 0 ? "+" : ""}{item.averageUniquePrice.toFixed(1)}%
                </Typography>
              )}
            </Typography>

          </Box>
      </CardContent>
    </Card>
  );
} 