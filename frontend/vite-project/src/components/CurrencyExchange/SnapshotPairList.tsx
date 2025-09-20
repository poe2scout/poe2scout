import { Paper, CircularProgress, Alert, TableContainer, Table, TableHead, TableRow, TableCell, TableBody, TableSortLabel, TablePagination } from "@mui/material";
import { CurrencyExchangeSnapshot } from "../../pages/CurrencyExchangePage";
import { useLeague } from "../../contexts/LeagueContext";
import { useEffect, useMemo, useState } from "react";
import { SnapshotPairRow } from "./SnapshotPairRow";
import { fetchSnapshotPairs, SnapshotPair } from "./api";
import { useNavigate } from "react-router-dom";

interface SnapshotPairListProps {
  snapshot: CurrencyExchangeSnapshot;
}

type Order = "asc" | "desc";
type OrderBy = "pair" | "volume";

export function SnapshotPairList({ snapshot }: SnapshotPairListProps) {
  const { league } = useLeague();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [snapshotPairs, setSnapshotPairs] = useState<SnapshotPair[]>([]);
  const [order, setOrder] = useState<Order>("desc");
  const [orderBy, setOrderBy] = useState<OrderBy>("volume");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  useEffect(() => {
    const getPairs = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const fetchedPairs = await fetchSnapshotPairs(league);

        if (fetchedPairs) {
          setSnapshotPairs(fetchedPairs);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred.");
      } finally {
        setIsLoading(false);
      }
    };
    getPairs();
  }, [league, snapshot.Epoch]);

  const handleRequestSort = (property: OrderBy) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
    setPage(0)
  };

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handlePairClick = (pair: SnapshotPair) => {
    navigate(
      `/exchange/pair/${pair.CurrencyOne.itemId}/${pair.CurrencyTwo.itemId}`,
      { state: { pair } },
    );
  };

  const visiblePairs = useMemo(() => {
    const sorted = [...snapshotPairs].sort((a, b) => {
      let compareResult = 0;
      switch (orderBy) {
        case "pair":
          const nameA = `${a.CurrencyOne.text}/${a.CurrencyTwo.text}`;
          const nameB = `${b.CurrencyOne.text}/${b.CurrencyTwo.text}`;
          compareResult = nameA.localeCompare(nameB);
          break;
        case "volume":
        default:
          compareResult = a.Volume - b.Volume;
          break;
      }
      return order === "desc" ? -compareResult : compareResult;
    });

    return sorted.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  }, [snapshotPairs, order, orderBy, page, rowsPerPage]);

  if (isLoading) {
    return (
      <Paper elevation={3} sx={{ p: 2, height: 450, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <CircularProgress />
      </Paper>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Paper elevation={3} sx={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', height: '100%' }}>
      <TableContainer sx={{ flexGrow: 1 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell sortDirection={orderBy === 'pair' ? order : false}>
                <TableSortLabel
                  active={orderBy === 'pair'}
                  direction={orderBy === 'pair' ? order : 'asc'}
                  onClick={() => handleRequestSort('pair')}
                >
                  Trading Pair
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ width: '400px' }} align="right">Exchange Rate</TableCell>
              <TableCell align="right" sortDirection={orderBy === 'volume' ? order : false}>
                <TableSortLabel
                  active={orderBy === 'volume'}
                  direction={orderBy === 'volume' ? order : 'asc'}
                  onClick={() => handleRequestSort('volume')}
                >
                  Volume
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {visiblePairs.map((pair) => (
              <SnapshotPairRow
                key={`${pair.CurrencyOne.itemId}-${pair.CurrencyTwo.itemId}`}
                pair={pair}
                onPairClick={handlePairClick}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10, 25, 50, 100]}
        component="div"
        count={snapshotPairs.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
}

export default SnapshotPairList;
