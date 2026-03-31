import { Typography, Paper, Grid, Stack } from "@mui/material";
import { CurrencyExchangeSnapshot } from "../../pages/CurrencyExchangePage";
import { useLeague } from "../../contexts/LeagueContext";
import { FormatTimeFromEpoch } from "../FormatTime";

interface SnapshotHeaderProps {
  snapshot: CurrencyExchangeSnapshot;
}

const StatBox = ({ title, value }: { title: string; value: string }) => (
  <Stack>
    <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
      {title}
    </Typography>
    <Typography variant="h6" component="p">
      {value}
    </Typography>
  </Stack>
);

export function SnapshotHeader({ snapshot }: SnapshotHeaderProps) {
  const { league } = useLeague();

  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={5}>
          <Typography variant="h4" component="h1">
            {league.value} Market
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Last updated: {FormatTimeFromEpoch(snapshot.Epoch)}
          </Typography>
        </Grid>
        <Grid item xs={12} md={7}>
          <Stack direction="row" spacing={4} justifyContent={{ xs: 'flex-start', md: 'flex-end' }}>
            <StatBox title="Hourly Volume" value={`$${snapshot.Volume.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })} ex`} />
            <StatBox title="Market Cap" value={`$${snapshot.MarketCap.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })} ex`} />
          </Stack>
        </Grid>
      </Grid>
    </Paper>
  );
}

export default SnapshotHeader;