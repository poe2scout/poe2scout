import { useState, useEffect } from "react";
import {
  Box,
  Grid,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Paper,
  Tooltip,
  IconButton,
  Pagination,
  Stack,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import SortIcon from '@mui/icons-material/Sort';
import { useLeague } from "../contexts/LeagueContext";
import { BaseItemCard } from "../features/chance/BaseItemCard";
import { UniqueItemExtended, UniqueBaseItem, CurrencyItemExtended } from "../types"; 
import { PriceDisplay } from "../components/TableColumnComponents/PriceDisplay";
import { UniqueItemsGrid } from "../features/chance/UniqueItemsGrid";

interface UniqueItemsApiResponse {
  items: UniqueItemExtended[];
}

type SortField = 'price' | 'name' | 'uniquePrice'; // Matches backend SortOptions
type SortDirection = 'asc' | 'desc';

export function ChancePage() {
  const { league, loading: leagueLoading } = useLeague();
  const [selectedBaseItem, setSelectedBaseItem] = useState<UniqueBaseItem | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [baseItems, setBaseItems] = useState<UniqueBaseItem[]>([]);
  const [uniqueItems, setUniqueItems] = useState<UniqueItemExtended[]>([]);
  const [chanceOrbPrice, setChanceOrbPrice] = useState<number | null>(null);

  const [loadingBaseItems, setLoadingBaseItems] = useState(true);
  const [loadingUniqueItems, setLoadingUniqueItems] = useState(false);
  const [loadingChancePrice, setLoadingChancePrice] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [baseSortField, setBaseSortField] = useState<SortField>('price');
  const [baseSortDirection, setBaseSortDirection] = useState<SortDirection>('desc');

  // --- API Fetching ---
  const perPage = 25;
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);

  // Fetch Base Items
  useEffect(() => {
    if (!league) return;
    setLoadingBaseItems(true);
    setError(null);
    const sortedBy = baseSortDirection === 'desc' ? baseSortField : `-${baseSortField}`;
    fetch(`${import.meta.env.VITE_API_URL}/items/uniqueBaseItems?page=${currentPage}&perPage=${perPage}&league=${league.value}&sortedBy=${sortedBy}&search=${searchQuery}`)
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch base items");
        return res.json();
      })
      .then(data => {
        setBaseItems(data.items);
        setTotalPages(data.pages);
        if (!selectedBaseItem && data.items.length > 0) {
          setSelectedBaseItem(data.items[0]);
        }
      })
      .catch(err => setError(err.message))
      .finally(() => setLoadingBaseItems(false));
  }, [league, currentPage, baseSortField, baseSortDirection, searchQuery]);

  // Fetch Unique Items when Base Item changes
  useEffect(() => {
    if (!selectedBaseItem || !league || leagueLoading) {
      setUniqueItems([]); // Clear uniques if no base item selected
      return;
    }
    setLoadingUniqueItems(true);
    setError(null);
    // --- Sketch of API Call ---
    const fetchUniqueItems = async () => {
        try {
          // Use the correct endpoint for uniques by base name
          const encodedName = encodeURIComponent(selectedBaseItem.name);
          const response = await fetch(
            `${import.meta.env.VITE_API_URL}/items/uniquesByBaseName/${encodedName}?league=${league.value}`
          );
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          const data: UniqueItemsApiResponse = await response.json(); // Assuming this structure
          setUniqueItems(data.items);
        } catch (err) {
          console.error("Failed to fetch unique items:", err);
          setError(err instanceof Error ? err.message : "Failed to load unique items.");
          setUniqueItems([]);
        } finally {
          setLoadingUniqueItems(false);
        }
      };
    fetchUniqueItems();
    // --- End Sketch ---
  }, [selectedBaseItem, league, leagueLoading]); // Refetch if selected item or league changes

  // Fetch Chance Orb Price
  useEffect(() => {
    if (!league || leagueLoading) return;
    setLoadingChancePrice(true);
    // --- Sketch of API Call ---
    const fetchChancePrice = async () => {
        try {
            // Leverage existing currency endpoint if possible
            const response = await fetch(`${import.meta.env.VITE_API_URL}/items/currencyById/chance?league=${league.value}`);
             if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
             const data: CurrencyItemExtended = (await response.json()).item;
             setChanceOrbPrice(data.currentPrice);
        } catch (err) {
            console.error("Failed to fetch Chance Orb price:", err);
            setChanceOrbPrice(null); // Set to null on error
        } finally {
            setLoadingChancePrice(false);
        }
    };
    fetchChancePrice();
    // --- End Sketch ---
  }, [league, leagueLoading]);

  const handlePageChange = (_: React.ChangeEvent<unknown>, page: number) => {
    setCurrentPage(page);
  };

  if (leagueLoading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}><CircularProgress /></Box>;
  }
  if (!league) {
     return <Alert severity="warning">Please select a league.</Alert>;
  }

  return (
    <Box sx={{ 
      height: 'calc(100vh - 50px)', 
      display: 'flex', 
      flexDirection: 'column',
      p: { xs: 1, sm: 2, md: 3 } // Responsive padding
    }}>
       <Box sx={{ mb: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Chance Orb Base Items
            </Typography>
            <Typography color="text.secondary">
              View base items and their potential unique outcomes when using Chance Orbs. Select a base item to see all possible unique items.
            </Typography>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Grid container spacing={{ xs: 1, sm: 2, md: 3 }} sx={{ flexGrow: 1, overflow: 'hidden' }}>
            {/* Base Items Column */}
            <Grid item xs={12} md={5} lg={4} xl={3} sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              height: '100%',
              minWidth: 0 // Prevent flex items from overflowing
            }}>
                 <Box sx={{ display: 'flex', gap: { xs: 0.5, sm: 1 }, mb: 2 }}>
                    <TextField
                        placeholder="Search base items..."
                        variant="outlined"
                        size="small"
                        fullWidth
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <SearchIcon />
                            </InputAdornment>
                          ),
                        }}
                    />
                    <FormControl size="small" sx={{ minWidth: { xs: 100, sm: 120 } }}>
                        <InputLabel>Sort By</InputLabel>
                        <Select
                            value={baseSortField}
                            label="Sort By"
                            onChange={(e) => setBaseSortField(e.target.value as SortField)}
                        >
                          <MenuItem value="price">Price</MenuItem>
                          <MenuItem value="name">Name</MenuItem>
                          <MenuItem value="uniquePrice">Unique Price</MenuItem>
                        </Select>
                    </FormControl>
                    <IconButton onClick={() => setBaseSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')}>
                        {baseSortDirection === 'asc' ? <SortIcon sx={{ transform: 'scaleY(-1)' }}/> : <SortIcon />}
                    </IconButton>
                 </Box>

                 <Box sx={{ flexGrow: 1, overflowY: 'auto', pr: 1 }}>
                    {loadingBaseItems ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', pt: 5 }}><CircularProgress /></Box>
                    ) : baseItems.length > 0 ? (
                        <Grid container spacing={1}>
                            {baseItems.map((item) => (
                                <Grid item xs={12} key={item.id}>
                                    <BaseItemCard
                                        item={item}
                                        isSelected={selectedBaseItem?.id === item.id}
                                        onClick={() => setSelectedBaseItem(item)}
                                        league={league}
                                    />
                                </Grid>
                            ))}
                        </Grid>
                    ) : (
                         <Typography sx={{ textAlign: 'center', mt: 4, color: 'text.secondary' }}>No base items found.</Typography>
                    )}
                 </Box>

                 {/* Add pagination controls */}
                 <Stack spacing={2} sx={{ 
                   mt: 2, 
                   pb: 1,
                   display: 'flex',
                   alignItems: 'center',
                   borderTop: 1,
                   borderColor: 'divider',
                   pt: 2
                 }}>
                   <Pagination 
                     count={totalPages} 
                     page={currentPage}
                     onChange={handlePageChange}
                     color="primary"
                     size="small"
                     siblingCount={1}
                     boundaryCount={1}
                   />
                 </Stack>
            </Grid>

            {/* Unique Items Column */}
            <Grid item xs={12} md={7} lg={8} xl={9} sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              height: '100%',
              borderLeft: { md: 1 }, 
              borderColor: { md: 'divider' }, 
              pl: { md: 3 },
              minWidth: 0 // Prevent flex items from overflowing
            }}>
                {selectedBaseItem ? (
                    <>
                        <Box sx={{ mb: 2 }}>
                            <Typography variant="h5" component="h2" gutterBottom>
                                Unique Items from {selectedBaseItem.name}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexWrap: 'wrap' }}>
                                <Typography variant="body2" color="text.secondary">
                                    Base price:
                                </Typography>
                                <PriceDisplay currentPrice={selectedBaseItem.currentPrice} divinePrice={league.divinePrice} />
                                <Tooltip title="Current market price of the base item">
                                    <InfoOutlinedIcon sx={{ fontSize: '1rem', color: 'text.secondary', cursor: 'help' }} />
                                </Tooltip>
                            </Box>
                        </Box>

                        <Grid container spacing={{ xs: 1, sm: 2 }} sx={{ mb: 2 }}>
                            <Grid item xs={6}>
                                <Card variant="outlined">
                                    <CardContent>
                                        <Typography variant="body2" color="text.secondary">Total Uniques</Typography>
                                        <Typography variant="h5" component="div" fontWeight="bold">
                                            {loadingUniqueItems ? <CircularProgress size={20} /> : uniqueItems.length}
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>
                             <Grid item xs={6}>
                                <Card variant="outlined">
                                    <CardContent>
                                        <Typography variant="body2" color="text.secondary">Chance Orb Price</Typography>
                                        <Box sx={{ display: 'flex', alignItems: 'center', minHeight: '28px' /* Align with Total Uniques */ }}>
                                            {loadingChancePrice ? <CircularProgress size={20} /> :
                                                <PriceDisplay currentPrice={chanceOrbPrice} divinePrice={league.divinePrice} />
                                            }
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>

                        {/* Unique Items Table/List */}
                        <Paper variant="outlined" sx={{ 
                          flexGrow: 1, 
                          display: 'flex', 
                          flexDirection: 'column', 
                          overflow: 'hidden',
                          minHeight: 0 // Ensure paper doesn't overflow
                        }}>
                             <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
                                {loadingUniqueItems ? (
                                    <Box sx={{ display: 'flex', justifyContent: 'center', pt: 5 }}><CircularProgress /></Box>
                                ) : uniqueItems.length > 0 ? (
                                    <UniqueItemsGrid items={uniqueItems} league={league} />
                                ) : (
                                    <Typography sx={{ textAlign: 'center', mt: 4, color: 'text.secondary' }}>
                                        No unique items found for this base.
                                    </Typography>
                                )}
                             </Box>
                        </Paper>
                    </>
                ) : (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'text.secondary' }}>
                        <Typography>Select a base item to see possible unique outcomes</Typography>
                    </Box>
                )}
            </Grid>
        </Grid>
    </Box>
  );
}

export default ChancePage; // Add default export if needed for routing 