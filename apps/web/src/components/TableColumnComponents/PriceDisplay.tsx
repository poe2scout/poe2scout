import { Box, Typography, Tooltip } from "@mui/material";
import { styled } from "@mui/material/styles";

import { getCurrencyIconUrl, getCurrencyLabel } from "../../currencyMeta";

interface PriceDisplayProps {
  currentPrice: number | null;
  divinePrice: number;
  referenceCurrency: string;
  referenceCurrencyText?: string;
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

const DIVINE_THRESHOLD = 1.2;

export function PriceDisplay({
  currentPrice,
  divinePrice,
  referenceCurrency,
  referenceCurrencyText,
}: PriceDisplayProps) {
  if (currentPrice === null || currentPrice === undefined) {
    return <Typography variant="body2">N/A</Typography>;
  }

  const showInDivine = divinePrice > 0 && (currentPrice / divinePrice) >= DIVINE_THRESHOLD;
  const displayPrice = showInDivine
    ? (currentPrice / divinePrice).toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      })
    : currentPrice.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      });

  const currencyName = getCurrencyLabel(referenceCurrency, referenceCurrencyText);

  const tooltipTitle = showInDivine
    ? `${currentPrice.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      })} ${currencyName} Equivalent`
    : `${displayPrice} ${currencyName}${currentPrice !== 1 ? 's' : ''}`;

  const baseIconUrl = getCurrencyIconUrl(referenceCurrency);
  const divineIconUrl = getCurrencyIconUrl("divine");
  return (
    <Tooltip title={tooltipTitle}>
      <PriceContainer>
        <Typography variant="body2">{displayPrice}</Typography>
        {(showInDivine ? divineIconUrl : baseIconUrl) ? (
          <CurrencyIcon
            src={(showInDivine ? divineIconUrl : baseIconUrl) ?? ""}
            alt={showInDivine ? "divine" : referenceCurrency}
          />
        ) : (
          <Typography variant="caption" color="text.secondary">
            {showInDivine ? "Div" : referenceCurrency}
          </Typography>
        )}
      </PriceContainer>
    </Tooltip>
  );
}
