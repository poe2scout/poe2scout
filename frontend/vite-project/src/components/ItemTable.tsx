import { useState, useMemo, useEffect } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TableSortLabel,
  TablePagination,
  Typography,
  Box,
  IconButton,
  Collapse,
  Stack,
} from "@mui/material";
import { styled, useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import TuneIcon from "@mui/icons-material/Tune";

import type {
  ApiItem,
  CurrencyItemExtended,
  UniqueItemExtended,
  PaginatedResponse,
  Category,
} from "../types";
import CircularProgress from "@mui/material/CircularProgress";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { PriceDisplay } from "./TableColumnComponents/PriceDisplay";
import { PriceHistory } from "./TableColumnComponents/PriceHistory";
import { ItemName } from "./TableColumnComponents/ItemName";
import { ItemDetail } from "./ItemDetail";
import translations from "../translationskrmapping.json";
import { SearchAutocomplete } from "./SearchAutocomplete";
import { useNavigate } from "react-router-dom";
import { useLeague, League } from "../contexts/LeagueContext";
import { useCategories } from "../contexts/CategoryContext";
import { useSearchableItems } from "../hooks/useSearchableItems";
import ReferenceCurrencySelector from "./ReferenceCurrencySelector";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

type Order = "asc" | "desc";
type OrderBy = "name" | "price";

const ItemRow = styled(TableRow)(({ }) => ({
  ".MuiTableRow-root": {
    padding: '200px'
  }
}));

const TableOptions = styled(Box)(({ }) => ({
  display: 'flex'
}))

const StyledTableCell = styled(TableCell)(() => ({
  padding: '8px'
}))


const ActionLink = styled("a")(({ theme }) => ({
  color: theme.palette.text.secondary,
  textDecoration: "none",
  fontSize: "0.85em",
  display: "block",
  padding: "2px 0",
  transition: "color 0.2s",
  "&:hover": {
    color: theme.palette.primary.main,
  },
}));

const ActionContainer = styled("div")({
  display: "flex",
  flexDirection: "row",
  alignItems: "center",
  gap: "2px",
});

interface ItemTableProps {
  type: string;
  language?: "en" | "ko";
  initialSearch?: string;
}

const getWikiUrl = (item: ApiItem) => {
  const wikiNameSource = 'name' in item ? item.name : item.text;
  const wikiName = encodeURIComponent(wikiNameSource);
  return `https://www.poe2wiki.net/wiki/${wikiName}`;
};

const getTradeUrl = (item: ApiItem, league: League) => {
  const isUnique = "name" in item;
  const isCurrency = "currencyCategoryId" in item;

  if (isCurrency) {
    const currencyItem = item as CurrencyItemExtended;
    return `https://www.pathofexile.com/trade2/exchange/poe2/${league.value.toLowerCase()}?q=${encodeURIComponent(
      JSON.stringify({
        exchange: {
          status: { option: "online" },
          have: ["exalted"],
          want: [currencyItem.apiId],
        },
      })
    )}`;
  } else {
    const searchTerm = isUnique ? (item as UniqueItemExtended).name : (item as CurrencyItemExtended).apiId;
    return `https://www.pathofexile.com/trade2/search/${league.value.toLowerCase()}?q=${encodeURIComponent(
      JSON.stringify({
        query: {
          filters: {},
          [isUnique ? "name" : "type"]: searchTerm,
        },
      })
    )}`;
  }
};

export function ItemTable({ type, language, initialSearch }: ItemTableProps) {
  const navigate = useNavigate();
  const { league } = useLeague();
  const { currencyCategories } = useCategories();
  const [items, setItems] = useState<ApiItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalItems, setTotalItems] = useState(0);
  const [order, setOrder] = useState<Order>("desc");
  const [orderBy, setOrderBy] = useState<OrderBy>("price");
  const [referenceCurrency, setReferenceCurrency] = useState<"exalted" | "chaos">("exalted")
  const [itemSelection, setItemSelection] = useState<{
    item: ApiItem | null;
    scrollPosition: number;
  }>({
    item: null,
    scrollPosition: 0,
  });

  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down("lg"));
  const [filtersOpen, setFiltersOpen] = useState(Boolean(initialSearch));

  useEffect(() => {
    if (initialSearch) {
      setFiltersOpen(true);
    }
  }, [initialSearch]);

  const {
    searchableItems,
    loading: loadingSearchable,
    error: errorSearchable
  } = useSearchableItems();

  useEffect(() => {
    setItemSelection({
      item: null,
      scrollPosition: 0,
    });
  }, [type, league]);

  const fetchItems = async (currentPage: number, perPage: number, search: string = "") => {
    setLoading(true);
    const isCurrencyType = currencyCategories.some((cat: Category) => cat.apiId === type);
    const endpointType = isCurrencyType ? "currency" : "unique";

    const apiUrl = `${
      import.meta.env.VITE_API_URL
    }/items/${endpointType}/${type}?page=${currentPage}&perPage=${perPage}&league=${league.value}&search=${search}&referenceCurrency=${referenceCurrency}`;

    try {
      const response = await fetch(apiUrl);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: PaginatedResponse<UniqueItemExtended | CurrencyItemExtended> =
        await response.json();

      const itemsWithType: ApiItem[] = data.items.map((item: UniqueItemExtended | CurrencyItemExtended) => ({
        ...item,
      }));

      setItems(itemsWithType);
      setTotalItems(data.total);
    } catch (error) {
      console.error("Error fetching items:", error);
      setItems([]);
      setTotalItems(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(0);
    fetchItems(1, rowsPerPage, initialSearch || "");
  }, [initialSearch, type, league, rowsPerPage, referenceCurrency]);

  const handleRequestSort = (property: OrderBy) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
    fetchItems(newPage + 1, rowsPerPage, initialSearch);
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPage(newRowsPerPage);
    setPage(0);
    fetchItems(1, newRowsPerPage, initialSearch);
  };

  const sortedItems = useMemo(() => {
    return [...items].sort((a: ApiItem, b: ApiItem) => {
      let compareResult = 0;

      switch (orderBy) {
        case "name":
          const nameA = "name" in a ? a.name : a.text;
          const nameB = "name" in b ? b.name : b.text;
          compareResult = nameA.localeCompare(nameB);
          break;
        case "price":
          const priceA = a.currentPrice ?? 0;
          const priceB = b.currentPrice ?? 0;
          compareResult = priceA - priceB;
          break;
        default:
          compareResult = 0;
      }

      return order === "desc" ? -compareResult : compareResult;
    });
  }, [items, order, orderBy]);

  const filteredItems = sortedItems;

  const handleItemSelect = (item: ApiItem) => {
    const tableContainer = document.querySelector(".MuiTableContainer-root");
    setItemSelection({
      item,
      scrollPosition: tableContainer?.scrollTop || 0,
    });
  };

  const getTranslatedText = (key: string, language: "en" | "ko" = "en") => {
    if (language === "ko" && key in translations) {
      return translations[key as keyof typeof translations];
    }
    return key;
  };

  const handleClearSearch = () => {
    navigate(`/economy/${type}`);
    setPage(0);
    fetchItems(1, rowsPerPage, "");
  };

  if (itemSelection.item) {
    return (
      <ItemDetail
        item={itemSelection.item}
        initialReferenceCurrency={referenceCurrency}
        onBack={() => {
          setItemSelection((prev) => ({
            item: null,
            scrollPosition: prev.scrollPosition,
          }));
          requestAnimationFrame(() => {
            const tableContainer = document.querySelector(
              ".MuiTableContainer-root"
            );
            if (tableContainer) {
              tableContainer.scrollTop = itemSelection.scrollPosition;
            }
          });
        }}
      />
    );
  }

  return (
    <Paper
      sx={{
        height: "93vh",
        display: "flex",
        flexDirection: "column",
        minWidth: "800px",
      }}
    >        
      <TableOptions>

      </TableOptions>
      <TableContainer
        sx={{ flexGrow: 1, overflowX: "auto", minWidth: "800px" }}
      >
        <Table
          stickyHeader
          sx={{
            "& .MuiTableHead-root .MuiTableCell-root": {
              backgroundColor: (theme) =>
                theme.palette.mode === "dark" ? "#1e1e1e" : "#fff",
            },
            tableLayout: "fixed",
            width: "100%",
          }}
        >
          <TableHead>
            <TableRow>
              <StyledTableCell
                sx={{
                  minWidth: "150px",
                  width: "auto",
                  overflow: "hidden",
                }}
              >
                <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', position: 'relative', flexGrow: 1, minWidth: 0 }}>
                      <TableSortLabel
                        active={orderBy === "name"}
                        direction={orderBy === "name" ? order : "asc"}
                        onClick={() => handleRequestSort("name")}
                      >
                        {getTranslatedText("Item", language)}
                      </TableSortLabel>
                      {errorSearchable && (
                        <Typography
                          color="error"
                          variant="caption"
                          sx={{ position: 'absolute', bottom: '-18px' }}
                        >
                          Error loading items
                        </Typography>
                      )}
                    </Box>
                    <IconButton
                      onClick={() => setFiltersOpen((prev) => !prev)}
                      sx={{ ml: 1 }}
                      aria-label={filtersOpen ? "Hide table filters" : "Show table filters"}
                      color={filtersOpen ? "primary" : "default"}
                    >
                      <TuneIcon />
                    </IconButton>
                  </Box>

                  <Collapse in={filtersOpen} timeout="auto" unmountOnExit>
                    <Stack
                      direction={isSmallScreen ? "column" : "row"}
                      spacing={2}
                      sx={{
                        pt: 2,
                        pb: isSmallScreen ? 1 : 0,
                        pr: isSmallScreen ? 2 : 0,
                        pl: isSmallScreen ? 2 : 0,
                        alignItems: isSmallScreen ? "stretch" : "center"
                      }}
                    >
                      <Box sx={{ flex: 1, minWidth: '200px' }}>
                        <SearchAutocomplete
                          searchableItems={searchableItems}
                          isLoadingList={loadingSearchable}
                          placeholder={`${getTranslatedText("Search", language)} ${getTranslatedText("Item", language)}`}
                          initialValue={initialSearch || ""}
                          onItemSelect={(category, localisationName) => {
                            const searchParam = encodeURIComponent(localisationName);
                            navigate(`/economy/${category}?search=${searchParam}`, { replace: true });
                          }}
                          onClear={handleClearSearch}
                        />
                      </Box>
                      <ReferenceCurrencySelector
                        currentReference={referenceCurrency}
                        onReferenceChange={(item) => setReferenceCurrency(item as 'exalted'| 'chaos')}
                        options={['exalted','chaos']}
                      />
                    </Stack>
                  </Collapse>
                </Box>
              </StyledTableCell>
              <StyledTableCell
                sx={{
                  width: "120px",
                  minWidth: "120px",
                  maxWidth: "120px",
                }}
              >
                <TableSortLabel
                  active={orderBy === "price"}
                  direction={orderBy === "price" ? order : "asc"}
                  onClick={() => handleRequestSort("price")}
                >
                  {getTranslatedText("Price", language)}
                </TableSortLabel>
              </StyledTableCell>
              <StyledTableCell
                sx={{
                  width: "80px",
                  minWidth: "80px",
                  maxWidth: "80px",
                }}
              >
                {getTranslatedText("Quantity", language)}
              </StyledTableCell>
              <StyledTableCell
                sx={{
                  width: "250px",
                  minWidth: "250px",
                  maxWidth: "250px",
                  textAlign: "center",
                }}
              >
                {getTranslatedText("Price History", language)}
              </StyledTableCell>
              <StyledTableCell
                sx={{
                  width: "100px",
                  minWidth: "100px",
                  maxWidth: "100px",
                  textAlign: "center",
                }}
              >
                {getTranslatedText("Actions", language)}
              </StyledTableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <StyledTableCell
                  colSpan={5}
                  align="center"
                  style={{ padding: "40px" }}
                >
                  <CircularProgress />
                </StyledTableCell>
              </TableRow>
            ) : (
              filteredItems.map((item: ApiItem) => (
                <ItemRow key={item.id}>
                  <StyledTableCell>
                    <div
                      onClick={() => handleItemSelect(item)}
                      style={{ cursor: "pointer" }}
                    >
                      <ItemName
                        iconUrl={item.iconUrl}
                        name={"name" in item ? item.name : item.text}
                        isUnique={"name" in item}
                        itemMetadata={item.itemMetadata}
                      />
                    </div>
                  </StyledTableCell>
                  <StyledTableCell>
                    <PriceDisplay currentPrice={item.currentPrice} divinePrice={referenceCurrency == 'exalted' ? league.exaltedDivinePrice : league.chaosDivinePrice} referenceCurrency={referenceCurrency}/>
                  </StyledTableCell>
                  <StyledTableCell>
                    {item.priceLogs?.[0]?.quantity ?? "N/A"}
                  </StyledTableCell>
                  <StyledTableCell
                    sx={{
                      display: { md: "table-cell" },
                    }}
                  >
                    {item.priceLogs != null && item.priceLogs.length > 0 && (
                      <PriceHistory priceHistory={item.priceLogs} variant="table" />
                    )}
                  </StyledTableCell>
                  <StyledTableCell align="center">
                    <ActionContainer>
                      <ActionLink
                        href={getWikiUrl(item)}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {getTranslatedText("Wiki", language)}
                      </ActionLink>
                      /
                      <ActionLink
                        href={getTradeUrl(item, league)}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {getTranslatedText("Trade", language)}
                      </ActionLink>
                    </ActionContainer>
                  </StyledTableCell>
                </ItemRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        component="div"
        count={totalItems}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[10, 25, 50, 100]}
        sx={{
          flexShrink: 0,
          ".MuiTablePagination-toolbar": {
            minHeight: "40px",
            paddingY: "4px",
          },
          ".MuiTablePagination-selectLabel, .MuiTablePagination-displayedRows":
            {
              margin: 0,
            },
        }}
      />
    </Paper>
  );
}
