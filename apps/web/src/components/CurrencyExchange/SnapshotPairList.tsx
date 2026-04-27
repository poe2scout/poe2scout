import {
  Paper,
  CircularProgress,
  Alert,
  Box,
  IconButton,
  InputAdornment,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableSortLabel,
  TablePagination,
  TextField,
  Typography,
} from "@mui/material";
import ClearIcon from "@mui/icons-material/Clear";
import SearchIcon from "@mui/icons-material/Search";
import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useLeague } from "../../contexts/LeagueContext";
import type { CurrencyExchangeSnapshot, SnapshotPair } from "../../types";
import { fetchSnapshotPairs } from "./api";
import { SnapshotPairRow } from "./SnapshotPairRow";

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
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("");
  const searchDebounceTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    const getPairs = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const fetchedPairs = await fetchSnapshotPairs(league.value);

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
  }, [league, snapshot.epoch]);

  const scheduleSearchUpdate = (value: string) => {
    if (searchDebounceTimeoutRef.current !== null) {
      window.clearTimeout(searchDebounceTimeoutRef.current);
    }

    searchDebounceTimeoutRef.current = window.setTimeout(() => {
      setDebouncedSearchTerm(value.trim().toLowerCase());
      setPage(0);
      searchDebounceTimeoutRef.current = null;
    }, 250);
  };

  const handleSearchChange = (value: string) => {
    setSearchInput(value);
    scheduleSearchUpdate(value);
  };

  const handleSearchClear = () => {
    if (searchDebounceTimeoutRef.current !== null) {
      window.clearTimeout(searchDebounceTimeoutRef.current);
      searchDebounceTimeoutRef.current = null;
    }

    setSearchInput("");
    setDebouncedSearchTerm("");
    setPage(0);
  };

  const handleRequestSort = (property: OrderBy) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
    setPage(0);
  };

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handlePairClick = (pair: SnapshotPair) => {
    navigate(
      `/exchange/pair/${pair.currencyOne.itemId}/${pair.currencyTwo.itemId}`,
      { state: { pair } },
    );
  };

  const filteredPairs = useMemo(() => {
    if (!debouncedSearchTerm) {
      return snapshotPairs;
    }

    return snapshotPairs.filter((pair) => {
      const pairSearchText = [
        pair.currencyOne.text,
        pair.currencyTwo.text,
        pair.currencyOne.apiId,
        pair.currencyTwo.apiId,
        `${pair.currencyOne.text}/${pair.currencyTwo.text}`,
        `${pair.currencyOne.text} / ${pair.currencyTwo.text}`,
        `${pair.currencyOne.apiId}/${pair.currencyTwo.apiId}`,
        `${pair.currencyOne.apiId} / ${pair.currencyTwo.apiId}`,
      ].join(" ").toLowerCase();

      return pairSearchText.includes(debouncedSearchTerm);
    });
  }, [snapshotPairs, debouncedSearchTerm]);

  const visiblePairs = useMemo(() => {
    const sorted = [...filteredPairs].sort((a, b) => {
      let compareResult = 0;
      switch (orderBy) {
        case "pair": {
          const nameA = `${a.currencyOne.text}/${a.currencyTwo.text}`;
          const nameB = `${b.currencyOne.text}/${b.currencyTwo.text}`;
          compareResult = nameA.localeCompare(nameB);
          break;
        }
        case "volume":
        default:
          compareResult = a.volume - b.volume;
          break;
      }
      return order === "desc" ? -compareResult : compareResult;
    });

    return sorted.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  }, [filteredPairs, order, orderBy, page, rowsPerPage]);

  if (isLoading) {
    return (
      <Paper
        elevation={3}
        sx={{
          p: 2,
          height: 450,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <CircularProgress />
      </Paper>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Paper
      elevation={3}
      sx={{
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        height: "100%",
      }}
    >
      <Box sx={{ p: 2, pb: 1 }}>
        <TextField
          value={searchInput}
          onChange={(event) => handleSearchChange(event.target.value)}
          placeholder="Search trading pairs"
          variant="outlined"
          size="small"
          fullWidth
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
            endAdornment: searchInput ? (
              <InputAdornment position="end">
                <IconButton
                  aria-label="Clear trading pair search"
                  edge="end"
                  size="small"
                  onClick={handleSearchClear}
                >
                  <ClearIcon fontSize="small" />
                </IconButton>
              </InputAdornment>
            ) : null,
          }}
          inputProps={{
            "aria-label": "Search trading pairs",
            autoComplete: "off",
          }}
        />
      </Box>
      <TableContainer sx={{ flexGrow: 1 }}>
        <Table
          stickyHeader
          size="small"
          sx={{
            "& .MuiTableHead-root .MuiTableCell-root": {
              backgroundColor: (theme) =>
                theme.palette.mode === "dark" ? "#1e1e1e" : "#fff",
            },
          }}
        >
          <TableHead>
            <TableRow>
              <TableCell sortDirection={orderBy === "pair" ? order : false}>
                <TableSortLabel
                  active={orderBy === "pair"}
                  direction={orderBy === "pair" ? order : "asc"}
                  onClick={() => handleRequestSort("pair")}
                >
                  Trading Pair
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ width: "400px" }} align="right">
                Exchange Rate
              </TableCell>
              <TableCell
                align="right"
                sortDirection={orderBy === "volume" ? order : false}
              >
                <TableSortLabel
                  active={orderBy === "volume"}
                  direction={orderBy === "volume" ? order : "asc"}
                  onClick={() => handleRequestSort("volume")}
                >
                  Volume
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {visiblePairs.length > 0 ? (
              visiblePairs.map((pair) => (
                <SnapshotPairRow
                  key={`${pair.currencyOne.itemId}-${pair.currencyTwo.itemId}`}
                  pair={pair}
                  onPairClick={handlePairClick}
                />
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} align="center" sx={{ py: 6 }}>
                  <Typography variant="body2" color="text.secondary">
                    No trading pairs match your search.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10, 25, 50, 100]}
        component="div"
        count={filteredPairs.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
}

export default SnapshotPairList;
