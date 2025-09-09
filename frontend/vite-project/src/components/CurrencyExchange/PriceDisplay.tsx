import { Box, Typography, TableCell } from "@mui/material";
import { SnapshotPair } from "./SnapshotPairList";


interface PriceDisplayProps {
  isHovered: boolean;
  pair: SnapshotPair;
}

interface PriceDisplayProp {
  iconUrl: string;
  itemPrice: number;
}

function PriceDisplay({iconUrl, itemPrice}: PriceDisplayProp){
  return (
    <Box 
      component="span" 
      sx={{ 
        display: 'inline-flex', 
        alignItems: 'center', 
        fontWeight: 'medium' 
      }}
    >
      {itemPrice.toFixed(2)} 
      <img 
        style={{ width: '30px', marginLeft: '0.25em' }} 
        src={iconUrl}
      />
    </Box>   )}


export function CurrencyExchangePriceDisplay({ isHovered, pair }: PriceDisplayProps) {
  const item1Price = pair.CurrencyTwoData.VolumeTraded / pair.CurrencyOneData.VolumeTraded;
  const item2Price = pair.CurrencyOneData.VolumeTraded / pair.CurrencyTwoData.VolumeTraded;
  return (
    <TableCell align="right" sx={{ py: 1 }}>
    <Typography variant="body2" noWrap component="div">
        {isHovered ? (
        <Box>
            <PriceDisplay iconUrl={pair.CurrencyTwo.iconUrl ?? ''} itemPrice={1.00} /> = <PriceDisplay iconUrl={pair.CurrencyOne.iconUrl ?? ''} itemPrice={item2Price} />
        </Box>
        ) : (
        <>
            <PriceDisplay iconUrl={pair.CurrencyOne.iconUrl ?? ''} itemPrice={1.00} /> = <PriceDisplay iconUrl={pair.CurrencyTwo.iconUrl ?? ''} itemPrice={item1Price} />
        </>
        )}
    </Typography>
    </TableCell>
  );
}
