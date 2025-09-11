import { Paper, CircularProgress, Alert, TableContainer, Table, TableHead, TableRow, TableCell, TableBody, TableSortLabel, TablePagination } from "@mui/material";
import { CurrencyExchangeSnapshot } from "../../pages/CurrencyExchangePage";
import { League, useLeague } from "../../contexts/LeagueContext";
import { VITE_API_URL } from "./SnapshotHistory";
import { CurrencyItem } from "../../types";
import { useEffect, useMemo, useState } from "react";
import { BaseCurrencyList } from "../ReferenceCurrencySelector";
import { SnapshotPairRow } from "./SnapshotPairRow";

interface SnapshotPairListProps {
  snapshot: CurrencyExchangeSnapshot;
}

interface CurrencyPairDataDto {
  ValueTraded: string;
  RelativePrice: string;
  StockValue: string;
  VolumeTraded: number;
  HighestStock: number;
}

interface SnapshotPairDto {
  Volume: string;
  CurrencyOne: CurrencyItem;
  CurrencyTwo: CurrencyItem;
  CurrencyOneData: CurrencyPairDataDto;
  CurrencyTwoData: CurrencyPairDataDto;
}

interface CurrencyPairData {
  ValueTraded: number;
  RelativePrice: number;
  StockValue: number;
  VolumeTraded: number;
  HighestStock: number;
}

export interface SnapshotPair {
  Volume: number;
  CurrencyOne: CurrencyItem;
  CurrencyTwo: CurrencyItem;
  CurrencyOneData: CurrencyPairData;
  CurrencyTwoData: CurrencyPairData;
}

type Order = "asc" | "desc";
type OrderBy = "pair" | "volume";


const fetchSnapshotPairs = async (league: League): Promise<SnapshotPair[]> => {
  const response = await fetch(`${VITE_API_URL}/currencyExchange/SnapshotPairs?league=${league.value}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch data: ${response.statusText}`);
  }
  const rows: SnapshotPairDto[] = await response.json();

  return rows.map((row) => {
    const currencyOneData: CurrencyPairData = {
      ValueTraded: parseFloat(row.CurrencyOneData.ValueTraded),
      RelativePrice: parseFloat(row.CurrencyOneData.RelativePrice),
      StockValue: parseFloat(row.CurrencyOneData.StockValue),
      VolumeTraded: row.CurrencyOneData.VolumeTraded,
      HighestStock: row.CurrencyOneData.HighestStock
    }
    const currencyTwoData: CurrencyPairData = {
      ValueTraded: parseFloat(row.CurrencyTwoData.ValueTraded),
      RelativePrice: parseFloat(row.CurrencyTwoData.RelativePrice),
      StockValue: parseFloat(row.CurrencyTwoData.StockValue),
      VolumeTraded: row.CurrencyTwoData.VolumeTraded,
      HighestStock: row.CurrencyTwoData.HighestStock
    }

    const isCurrencyOneBase = BaseCurrencyList.includes(row.CurrencyOne.apiId);

    const areBothCurrencyBases = BaseCurrencyList.includes(row.CurrencyOne.apiId) && BaseCurrencyList.includes(row.CurrencyTwo.apiId)

    if (areBothCurrencyBases) {
      const isCorrectOrder = currencyOneData.VolumeTraded <= currencyTwoData.VolumeTraded

      if (isCorrectOrder) {
        return {
          Volume: parseFloat(row.Volume),
          CurrencyOne: row.CurrencyOne,
          CurrencyTwo: row.CurrencyTwo,
          CurrencyOneData: currencyOneData,
          CurrencyTwoData: currencyTwoData
        }
      }
      else {
        return {
          Volume: parseFloat(row.Volume),
          CurrencyOne: row.CurrencyTwo,
          CurrencyTwo: row.CurrencyOne,
          CurrencyOneData: currencyTwoData,
          CurrencyTwoData: currencyOneData
        }
      }
    }
    if (!isCurrencyOneBase) {
      return {
        Volume: parseFloat(row.Volume),
        CurrencyOne: row.CurrencyOne,
        CurrencyTwo: row.CurrencyTwo,
        CurrencyOneData: currencyOneData,
        CurrencyTwoData: currencyTwoData
      }
    }

    return {
      Volume: parseFloat(row.Volume),
      CurrencyOne: row.CurrencyTwo,
      CurrencyTwo: row.CurrencyOne,
      CurrencyOneData: currencyTwoData,
      CurrencyTwoData: currencyOneData
    }
  })
}

export function SnapshotPairList({ snapshot }: SnapshotPairListProps) {
  const { league } = useLeague();
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
    console.log("Navigating to history for:", `${pair.CurrencyOne.text} / ${pair.CurrencyTwo.text}`);
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
            {visiblePairs.map((pair) => {
              return (
                <SnapshotPairRow pair={pair} onPairClick={handlePairClick} />
              );
            })}
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