import { Box, Typography, Tooltip } from "@mui/material";
import { styled } from "@mui/material/styles";

interface PriceDisplayProps {
  currentPrice: number | null;
  divinePrice: number;
  referenceCurrency: "exalted" | "chaos"
}

const PriceContainer = styled(Box)({
  display: "flex",
  justifyContent: "flex-end",
  gap: "4px",
});

const CurrencyIcon = styled("img")({
  width: "24px",
  height: "24px",
  verticalAlign: "middle",
});

const EXALTED_ORB_ICON_URL = "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lBZGRNb2RUb1JhcmUiLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/ad7c366789/CurrencyAddModToRare.png"; // Update with actual path
const CHAOS_ORB_ICON_URL = "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lSZXJvbGxSYXJlIiwic2NhbGUiOjEsInJlYWxtIjoicG9lMiJ9XQ/c0ca392a78/CurrencyRerollRare.png"
const DIVINE_ORB_ICON_URL = "https://web.poecdn.com//gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvQ3VycmVuY3lNb2RWYWx1ZXMiLCJzY2FsZSI6MSwicmVhbG0iOiJwb2UyIn1d/2986e220b3/CurrencyModValues.png";

const DIVINE_THRESHOLD = 1.2;

export function PriceDisplay({ currentPrice, divinePrice, referenceCurrency }: PriceDisplayProps) {
  if (currentPrice === null || currentPrice === undefined) {
    return <Typography variant="body2">N/A</Typography>;
  }

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

  const currencyName = referenceCurrency == "exalted"? "Exalted Orb" : "Chaos Orb"

  const tooltipTitle = showInDivine
    ? `${currentPrice.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      })} ${currencyName} Equivalent`
    : `${displayPrice} ${currencyName}${currentPrice !== 1 ? 's' : ''}`;


  const BASE_ICON_URL = referenceCurrency == "exalted" ? EXALTED_ORB_ICON_URL : CHAOS_ORB_ICON_URL;
  console.log(BASE_ICON_URL)
  return (
    <Tooltip title={tooltipTitle}>
      <PriceContainer>
        <Typography variant="body2">{displayPrice}</Typography>
        <CurrencyIcon
          src={showInDivine ? DIVINE_ORB_ICON_URL : BASE_ICON_URL}
          alt={showInDivine ? "div" : "ex"}
        />
      </PriceContainer>
    </Tooltip>
  );
}
