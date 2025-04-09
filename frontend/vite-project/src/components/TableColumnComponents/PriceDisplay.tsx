import { Box, Typography, Tooltip } from "@mui/material";
import { styled } from "@mui/material/styles";
// Assuming you have an Exalted Orb icon component or URL
// import ExaltedOrbIcon from './ExaltedOrbIcon.png';

// Define props based on new data structure
interface PriceDisplayProps {
  currentPrice: number | null;
  divinePrice: number;
}

const PriceContainer = styled(Box)({
  display: "flex",
  alignItems: "center",
  gap: "4px",
});

// Basic component for the icon, replace with actual implementation
const CurrencyIcon = styled("img")({
  width: "24px",
  height: "24px",
  verticalAlign: "middle",
});

// Placeholder URL for Exalted Orb icon
const EXALTED_ORB_ICON_URL = "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lBZGRNb2RUb1JhcmUiLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/ad7c366789/CurrencyAddModToRare.png"; // Update with actual path
const DIVINE_ORB_ICON_URL = "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lNb2RWYWx1ZXMiLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/2986e220b3/CurrencyModValues.png";

const DIVINE_THRESHOLD = 1.2;

export function PriceDisplay({ currentPrice, divinePrice }: PriceDisplayProps) {
  if (currentPrice === null || currentPrice === undefined) {
    return <Typography variant="body2">N/A</Typography>;
  }

  // Calculate if we should show in divine
  const showInDivine = (currentPrice/divinePrice) >= DIVINE_THRESHOLD;
  const displayPrice = showInDivine
    ? (currentPrice / divinePrice).toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      })
    : currentPrice.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      });

  const tooltipTitle = showInDivine
    ? `${currentPrice.toLocaleString()} Exalted Orb Equivalent`
    : `${displayPrice} Exalted Orb${currentPrice !== 1 ? 's' : ''}`;

  return (
    <Tooltip title={tooltipTitle}>
      <PriceContainer>
        <Typography variant="body2">{displayPrice}</Typography>
        <CurrencyIcon
          src={showInDivine ? DIVINE_ORB_ICON_URL : EXALTED_ORB_ICON_URL}
          alt={showInDivine ? "div" : "ex"}
        />
      </PriceContainer>
    </Tooltip>
  );
}
