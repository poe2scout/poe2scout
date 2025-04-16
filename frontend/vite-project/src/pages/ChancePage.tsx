import { useState, useEffect } from "react";
import {
  Box,
  Grid2 as Grid,
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
  FormControlLabel,
  Switch,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import SortIcon from '@mui/icons-material/Sort';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
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

// Add this custom hook at the top of the file, before the ChancePage component
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export function ChancePage() {
  const { league, loading: leagueLoading } = useLeague();
  const [selectedBaseItem, setSelectedBaseItem] = useState<UniqueBaseItem | null>(null);
  const [searchInput, setSearchInput] = useState("");
  const debouncedSearch = useDebounce(searchInput, 500);
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

  const [showUnchanceable, setShowUnchanceable] = useState(false);
  const [isMobileExpanded, setIsMobileExpanded] = useState(false);

  // Fetch Base Items
  useEffect(() => {
    if (!league) return;
    setLoadingBaseItems(true);
    setError(null);
    const sortedBy = baseSortDirection === 'desc' ? baseSortField : `-${baseSortField}`;
    fetch(`${import.meta.env.VITE_API_URL}/items/uniqueBaseItems?page=${currentPage}&perPage=${perPage}&league=${league.value}&sortedBy=${sortedBy}&search=${debouncedSearch}&showUnChanceable=${showUnchanceable}`)
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
  }, [league, currentPage, baseSortField, baseSortDirection, debouncedSearch, showUnchanceable]);

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

  const handleBaseItemSelect = (item: UniqueBaseItem) => {
    setSelectedBaseItem(item);
    // On mobile, expand the view when selecting an item
    if (window.innerWidth < 900) { // md breakpoint
      setIsMobileExpanded(true);
    }
  };

  if (leagueLoading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}><CircularProgress /></Box>;
  }
  if (!league) {
     return <Alert severity="warning">Please select a league.</Alert>;
  }

  return (
    <Box sx={{ 
      height: 'calc(100% - 10px)',
      display: 'flex', 
      flexDirection: 'column',
      p: { xs: 0.5, sm: 2, md: 3 }, // Reduced padding on mobile
      mb: { xs: 0, sm: 1 }
    }}>
       <Box> 
            <Typography marginBottom={0} fontSize={{ xs: '1.25rem', sm: '1.5rem', md: '2rem', lg: '3rem' }}>
              Chance Orb Base Outcomes
            </Typography>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}

        <Grid container spacing={{ xs: 0.5, sm: 2, md: 3 }} sx={{ flexGrow: 1, overflow: 'hidden' }}>
            {/* Base Items Column */}
            <Grid size={{xs: 12, md: 5, lg: 4, xl: 3}} 
              sx={{ 
                flexDirection: 'column', 
                height: '100%',
                minWidth: 0,
                display: { xs: isMobileExpanded ? 'none' : 'flex', md: 'flex' }
              }}
            >
                 <Box sx={{ 
                    display: 'flex', 
                    gap: { xs: 0.5, sm: 1.5 }, 
                    flexWrap: 'wrap',
                    mb: { xs: 0.5, sm: 1 }
                }}>
                    <TextField
                      margin="dense"
                      placeholder="Search base items..."
                      variant="outlined"
                      size="small"
                      sx={{ 
                          flexGrow: 1,
                          minWidth: { xs: '140px', sm: '200px' },  // Smaller on mobile
                          '& .MuiOutlinedInput-root': {
                            height: { xs: '32px', sm: '40px' }  // Smaller height on mobile
                          }
                      }}
                      value={searchInput}
                      onChange={(e) => setSearchInput(e.target.value)}
                      InputProps={{
                          startAdornment: (
                              <InputAdornment position="start">
                                  <SearchIcon sx={{ fontSize: { xs: '1.2rem', sm: '1.5rem' } }} />
                              </InputAdornment>
                          ),
                      }}
                    />
                    <FormControl margin="dense" size="small" sx={{ 
                        minWidth: { xs: '100px', sm: '140px' },
                        marginBottom: '0px',
                        '& .MuiOutlinedInput-root': {
                          height: { xs: '32px', sm: '40px' }
                        }
                    }}>
                        <InputLabel sx={{ 
                          fontSize: { xs: '0.8rem', sm: '1rem' },
                          lineHeight: { xs: '1rem', sm: 'inherit' }
                        }}>Sort By</InputLabel>
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
                </Box>
                <Box sx={{ 
                  display: 'flex', 
                  gap: 0.5, 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  mb: { xs: 0.5, sm: 1 }
                }}>
                    <IconButton 
                      size="small"
                      onClick={() => setBaseSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')}
                      sx={{ padding: { xs: 0.5, sm: 1 } }}
                    >
                        {baseSortDirection === 'asc' ? <SortIcon sx={{ transform: 'scaleY(-1)' }}/> : <SortIcon />}
                    </IconButton>
                    <FormControlLabel
                        sx={{ 
                          minWidth: 'auto',
                          marginRight: 0,
                          '& .MuiTypography-root': {
                            fontSize: { xs: '0.75rem', sm: '0.875rem' }
                          }
                        }}
                        control={
                            <Switch
                                size="small"
                                checked={showUnchanceable}
                                onChange={(e) => setShowUnchanceable(e.target.checked)}
                            />
                        }
                        label={
                            <Tooltip title="Show items that cannot be chanced">
                                <Typography variant="body2">Show All</Typography>
                            </Tooltip>
                        }
                    />
                </Box>

                 <Box sx={{ flexGrow: 1, overflowY: 'auto', pr: 1 }}>
                    {loadingBaseItems ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', pt: 5 }}><CircularProgress /></Box>
                    ) : baseItems.length > 0 ? (
                        <Grid container>
                            {baseItems.map((item) => (
                                <Grid size={{xs: 12}} key={item.id}>
                                    <BaseItemCard
                                        item={item}
                                        isSelected={selectedBaseItem?.id === item.id}
                                        onClick={() => handleBaseItemSelect(item)}
                                        league={league}
                                    />
                                </Grid>
                            ))}
                        </Grid>
                    ) : (
                         <Typography sx={{ textAlign: 'center', mt: 4, color: 'text.secondary' }}>No base items found.</Typography>
                    )}
                 </Box>
                 <Stack spacing={1} sx={{ 
                   pb: { xs: 0.5, sm: 1 },
                   pt: { xs: 0.5, sm: 1 },
                   display: 'flex',
                   alignItems: 'center',
                   borderTop: 1,
                   borderColor: 'divider',
                 }}>
                   <Pagination 
                     count={totalPages} 
                     page={currentPage}
                     onChange={handlePageChange}
                     color="primary"
                     size="small"
                     siblingCount={0}
                     boundaryCount={1}
                   />
                 </Stack>
            </Grid>

            {/* Unique Items Column */}
            <Grid size={{xs: 12, md: 7, lg: 8, xl: 9}} 
              sx={{ 
                flexDirection: 'column', 
                height: '100%',
                borderLeft: { md: 1 }, 
                borderColor: { md: 'divider' }, 
                pl: { md: 3 },
                minWidth: 0,
                display: { xs: isMobileExpanded ? 'flex' : 'none', md: 'flex' }
              }}
            >
                {selectedBaseItem ? (
                    <>
                        {/* Add back button for mobile */}
                        <Box sx={{ 
                          display: { xs: 'flex', md: 'none' }, 
                          mb: 2,
                          alignItems: 'center',
                          gap: 1
                        }}>
                          <IconButton 
                            onClick={() => setIsMobileExpanded(false)}
                            edge="start"
                          >
                            <ArrowBackIcon />
                          </IconButton>
                          <Typography variant="subtitle1">
                            Back to Base Items
                          </Typography>
                        </Box>

                        <Box sx={{ 
                            display: 'flex', 
                            mb: { xs: 1, sm: 2 }, 
                            alignItems: 'center', 
                            gap: { xs: 1, sm: 2 },
                            flexDirection: { xs: 'column', sm: 'row' },
                            width: '100%'
                        }}>
                            <Typography 
                                variant="h5" 
                                component="h2" 
                                sx={{ 
                                    fontSize: { xs: '1.25rem', sm: '1.5rem' },
                                    flexShrink: 0
                                }}
                            >
                                Unique Items from {selectedBaseItem.name}
                            </Typography>
                            
                            {/* Price cards in a row */}
                            <Box sx={{ 
                                display: 'flex', 
                                gap: { xs: 1, sm: 2 }, 
                                ml: { sm: 'auto' },
                                width: { xs: '100%', sm: 'auto' }
                            }}>
                                <Card variant="outlined" sx={{ 
                                    minWidth: { xs: 0, sm: 140 },
                                    flex: { xs: 1, sm: 'none' },
                                    flexWrap: { sm: 'wrap', md: 'nowrap' }
                                }}>
                                    <CardContent sx={{ 
                                        flex: { xs: 1, sm: 'none' },
                                        py: { xs: 0.5, sm: 1 }, 
                                        px: { xs: 1, sm: 2 },
                                        '&:last-child': { pb: { xs: 0.5, sm: 1 } }
                                    }}>
                                        <Typography 
                                            variant="body2" 
                                            color="text.secondary"
                                            sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                                        >
                                            Base price
                                        </Typography>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                            <PriceDisplay currentPrice={selectedBaseItem.currentPrice} divinePrice={league.divinePrice} />
                                            <Tooltip title="Current market price of the base item">
                                                <InfoOutlinedIcon sx={{ fontSize: { xs: '0.875rem', sm: '1rem' }, color: 'text.secondary', cursor: 'help' }} />
                                            </Tooltip>
                                        </Box>
                                    </CardContent>
                                </Card>

                                <Card variant="outlined" sx={{ 
                                    minWidth: { xs: 0, sm: 140 },
                                    flex: { xs: 1, sm: 'none' }
                                }}>
                                    <CardContent sx={{ 
                                        py: { xs: 0.5, sm: 1 }, 
                                        px: { xs: 1, sm: 2 },
                                        '&:last-child': { pb: { xs: 0.5, sm: 1 } }
                                    }}>
                                        <Typography 
                                            variant="body2" 
                                            color="text.secondary"
                                            sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                                        >
                                            Chance Orb Price
                                        </Typography>
                                        <Box sx={{ display: 'flex', alignItems: 'center', minHeight: { xs: '20px', sm: '24px' } }}>
                                            {loadingChancePrice ? <CircularProgress size={16} /> :
                                                <PriceDisplay currentPrice={chanceOrbPrice} divinePrice={league.divinePrice} />
                                            }
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Box>
                        </Box>
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