import { Box, Stack } from "@mui/material";
import { useOutletContext } from "react-router-dom";
import SnapshotHeader from "./SnapshotHeader";
import SnapshotHistory from "./SnapshotHistory";
import SnapshotPairList from "./SnapshotPairList";

export interface CurrencyExchangeSnapshot {
  Epoch: number;
  Volume: number;
  MarketCap: number;
}

export function CurrencyExchangeIndex() {
    const { snapshot } = useOutletContext<{ snapshot: CurrencyExchangeSnapshot }>();

    return (
    <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
        <Box sx={{ p: 2 }}>
        <Stack spacing={2}>
            <SnapshotHeader snapshot={snapshot} />
            <SnapshotHistory snapshot={snapshot} />
        </Stack>
        </Box>
        <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
        <SnapshotPairList snapshot={snapshot}></SnapshotPairList>
        </Box>
    </Box>
    );
}

export default CurrencyExchangeIndex;