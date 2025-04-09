import {
  Typography,
  Button,
  Container,
  Box,
  Grid2,
  Paper,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  CircularProgress,
  Alert,
  TextField,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import { useNavigate } from "react-router-dom";
import { ArrowForward as ArrowRight } from "@mui/icons-material";
import { useEffect, useState } from "react";
import {
  SearchAutocomplete,
} from "../components/SearchAutocomplete";
import { Link as RouterLink } from "react-router-dom";
import { useSearchableItems } from "../hooks/useSearchableItems";
import { FooterLink } from "../features/landing/FooterLink";

interface PriceLog {
  price: number;
  time: string;
  quantity: number;
}

interface SplashItem {
  id: number;
  itemId: number;
  currencyCategoryId: number;
  apiId: string;
  text: string;
  categoryApiId: string;
  iconUrl: string;
  itemMetadata: any;
  priceLogs: (PriceLog | null)[];
  currentPrice: number | null;
}

interface SplashInfoResponse {
  items: SplashItem[];
}

const getLatestPrice = (priceLogs: (PriceLog | null)[]): number | null => {
  for (let i = priceLogs.length - 1; i >= 0; i--) {
    if (priceLogs[i]?.price !== null && priceLogs[i]?.price !== undefined) {
      return priceLogs[i]!.price;
    }
  }
  return null;
};


const Footer = styled("footer")(({ theme }) => ({
  borderTop: `1px solid ${theme.palette.divider}`,
  padding: theme.spacing(6),
  marginTop: "auto",
  backgroundColor: theme.palette.mode === 'dark' ? 'grey.900' : theme.palette.background.paper,
  "& .footer-content": {
    display: "flex",
    justifyContent: "space-between",
    maxWidth: "1200px",
    margin: "0 auto",
    gap: theme.spacing(4),
    [theme.breakpoints.down("md")]: {
      flexDirection: "column",
      alignItems: "center",
      textAlign: "center",
    },
  },
  "& .footer-section": {
    flex: 1,
    minWidth: "200px",
  },
  "& .footer-links": {
    display: "flex",
    flexDirection: "column",
    gap: theme.spacing(1),
  },
  "& .footer-bottom": {
    borderTop: `1px solid ${theme.palette.divider}`,
    marginTop: theme.spacing(4),
    paddingTop: theme.spacing(2),
    textAlign: "center",
    color: theme.palette.text.secondary,
    fontSize: "0.875rem",
  },
}));

function LandingPage() {
  const navigate = useNavigate();
  const [splashItems, setSplashItems] = useState<SplashItem[]>([]);
  const [loadingSplash, setLoadingSplash] = useState<boolean>(true);
  const [errorSplash, setErrorSplash] = useState<string | null>(null);
  const {
    searchableItems,
    loading: loadingSearchable,
    error: errorSearchable,
  } = useSearchableItems();

  useEffect(() => {
    const fetchSplashData = async () => {
      setLoadingSplash(true);
      setErrorSplash(null);
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/items/landingSplashInfo`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: SplashInfoResponse = await response.json();
        setSplashItems(data.items.slice(0, 4));
      } catch (err) {
        console.error("Failed to fetch splash data:", err);
        setErrorSplash(
          err instanceof Error ? err.message : "An unknown error occurred"
        );
      } finally {
        setLoadingSplash(false);
      }
    };

    fetchSplashData();
  }, []);

  const handleSearchSelect = (category: string, identifier: string) => {
    navigate(`/economy/${category}?search=${identifier}`);
  };

  const handleSearchClear = () => {
  };

  const isLoading = loadingSplash || loadingSearchable;
  const fetchError = errorSplash || errorSearchable;

  return (
    <Box sx={{ bgcolor: "grey.950", color: "common.white", minHeight: "100vh", display: 'flex', flexDirection: 'column'}}>

      <Box component="main" sx={{ flexGrow: 1 }}>
        <Box sx={{ borderBottom: 1, borderColor: "grey.800", bgcolor: "grey.900", px: 4, py: { xs: 6, md: 10 } }}>
          <Container maxWidth="lg">
            <Grid2 container spacing={{ xs: 4, md: 6 }} alignItems="center">
              <Grid2 size={{ xs: 12, md: 6 }}>
                <Typography variant="h2" component="h1" sx={{ fontWeight: "bold", mb: 2 }}>
                  Poe2 Scout
                </Typography>
                <Typography variant="h5" sx={{ color: "grey.300", mb: 2 }}>
                  Your Ultimate Path of Exile 2 Companion
                </Typography>
                <Typography sx={{ color: "grey.400", mb: 4 }}>
                  Track market prices of items, currency, and more with up-to-date POE2 data
                </Typography>
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate("/economy/currency")}
                  endIcon={<ArrowRight />}
                  sx={{ bgcolor: 'primary.main', '&:hover': { bgcolor: 'primary.dark' } }}
                >
                  View Economy Data
                </Button>
              </Grid2>

              <Grid2 size={{ xs: 12, md: 6 }}>
                <Paper sx={{ bgcolor: "grey.950", p: 3, border: 1, borderColor: "grey.800", borderRadius: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="overline" sx={{ color: "grey.400" }}>League</Typography>
                    <Typography variant="overline" sx={{ color: "primary.light" }}>Economy</Typography>
                  </Box>
                  <TextField
                    value="Dawn of the Hunt"
                    variant="outlined"
                    size="small"
                    fullWidth
                    disabled
                    sx={{
                      mb: 3,
                      bgcolor: "grey.900",
                      input: { color: "common.white" },
                      '.MuiOutlinedInput-notchedOutline': { borderColor: 'grey.700' },
                      '&.Mui-disabled .MuiOutlinedInput-notchedOutline': { borderColor: 'grey.700' },
                      '&.Mui-disabled .MuiInputBase-input': { '-webkit-text-fill-color': 'rgba(255, 255, 255, 0.7)' },
                    }}
                  />

                  <Box sx={{ mb: 3 }}>
                    <SearchAutocomplete
                      searchableItems={searchableItems}
                      onItemSelect={handleSearchSelect}
                      onClear={handleSearchClear}
                      placeholder="Search Item..."
                      isLoadingList={loadingSearchable}
                    />
                    {errorSearchable && <Alert severity="error" sx={{ mt: 1 }}>Failed to load items for search.</Alert>}
                  </Box>

                  <Typography variant="body2" sx={{ color: "grey.400", mb: 1 }}>Popular Currency:</Typography>
                  <TableContainer component={Paper} sx={{ border: 1, borderColor: "grey.800", bgcolor: 'grey.900' }}>
                    <Table size="small">
                      <TableHead sx={{ bgcolor: 'grey.800' }}>
                        <TableRow>
                          <TableCell sx={{ color: "grey.400", borderBottomColor: 'grey.700' }}>Item</TableCell>
                          <TableCell align="right" sx={{ color: "grey.400", borderBottomColor: 'grey.700' }}>Price (Exalts)</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {isLoading ? (
                          <TableRow>
                            <TableCell colSpan={2} align="center" sx={{ borderBottom: 'none', py: 3 }}>
                              <CircularProgress size={77} />
                            </TableCell>
                          </TableRow>
                        ) : fetchError ? (
                          <TableRow>
                            <TableCell colSpan={2} align="center" sx={{ borderBottom: 'none', py: 2 }}>
                              <Typography color="error" variant="body2">Error loading items.</Typography>
                            </TableCell>
                          </TableRow>
                        ) : splashItems.length > 0 ? (
                          splashItems.map((item) => {
                            const latestPrice = getLatestPrice(item.priceLogs);
                            return (
                              <TableRow key={item.id} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                                <TableCell component="th" scope="row" sx={{ color: "common.white", borderBottomColor: 'grey.800' }}>
                                  {item.text}
                                </TableCell>
                                <TableCell align="right" sx={{ color: "common.white", borderBottomColor: 'grey.800' }}>
                                  {latestPrice !== null ? latestPrice : "N/A"}
                                </TableCell>
                              </TableRow>
                            );
                          })
                        ) : (
                          <TableRow>
                            <TableCell colSpan={2} align="center" sx={{ borderBottom: 'none', py: 2 }}>
                              <Typography color="textSecondary" variant="body2">No items to display.</Typography>
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid2>
            </Grid2>
          </Container>
        </Box>

        <Box sx={{ bgcolor: "grey.950", px: 4, py: 8 }}>
          <Container maxWidth="lg">
            <Grid2 container spacing={3}>
              {[
                { title: "Currency", desc: "Track all currency exchange rates", link: "/economy/currency" },
                { title: "Unique Items", desc: "Price check for unique gear", link: "/economy/unique" },
                { title: "GitHub", desc: "Developer information", link: "https://github.com/poe2scout/poe2scout", external: true },
                { title: "API Docs", desc: "Developer documentation", link: "/api/swagger", external: true },
              ].map((item) => (
                <Grid2 size={{ xs: 12, sm: 6, md: 3 }} key={item.title}>
                  <Paper
                    component={item.external ? 'a' : RouterLink}
                    {...(item.external
                      ? { href: item.link }
                      : { to: item.link })}
                    target={item.external ? '_blank' : undefined}
                    rel={item.external ? 'noopener noreferrer' : undefined}
                    sx={{
                      bgcolor: "grey.900",
                      p: 3,
                      border: 1,
                      borderColor: "grey.800",
                      borderRadius: 2,
                      textDecoration: 'none',
                      color: 'inherit',
                      display: 'block',
                      transition: 'transform 0.2s ease-in-out, background-color 0.2s ease-in-out',
                      '&:hover': {
                        bgcolor: "grey.800",
                        cursor: 'pointer',
                        transform: 'scale(1.03)',
                      }
                    }}
                  >
                    <Typography variant="h6" sx={{ color: "common.white", mb: 1 }}>{item.title}</Typography>
                    <Typography variant="body2" sx={{ color: "grey.400" }}>{item.desc}</Typography>
                  </Paper>
                </Grid2>
              ))}
            </Grid2>
          </Container>
        </Box>
      </Box>

      <Footer sx={{ bgcolor: "grey.950", borderTopColor: 'grey.800', mt: 'auto' }}>
        <div className="footer-content">
          <div className="footer-section">
            <Typography variant="h6" gutterBottom sx={{ color: 'common.white' }}>
              About
            </Typography>
            <Typography variant="body2" color="text.secondary">
              POE2 Scout is your go-to tool for price checking and market
              analysis in Path of Exile 2. We help you make informed trading
              decisions with real-time data.
            </Typography>
          </div>
          <div className="footer-section">
            <Typography variant="h6" gutterBottom sx={{ color: 'common.white' }}>
              Quick Links
            </Typography>
            <div className="footer-links">
              <FooterLink href="/economy/currency">
                Currency Exchange
              </FooterLink>
              <FooterLink href="/economy/unique">
                Unique Items
              </FooterLink>
              <FooterLink href="/api/swagger" external>
                API Docs
              </FooterLink>
            </div>
          </div>
          <div className="footer-section">
            <Typography variant="h6" gutterBottom sx={{ color: 'common.white' }}>
              Community
            </Typography>
            <div className="footer-links">
              <FooterLink href="https://github.com/poe2scout/poe2scout" external>
                GitHub
              </FooterLink>
              <FooterLink href="https://discord.gg/EHXVdQCpBq" external>
                Discord
              </FooterLink>
              <FooterLink href="#" external disabled>
                Support on Ko-fi (Soon)
              </FooterLink>
            </div>
          </div>
        </div>
        <div className="footer-bottom" style={{ borderTopColor: 'grey.800' }}>
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} POE2 Scout. Not affiliated with
            Grinding Gear Games.
          </Typography>
        </div>
      </Footer>
    </Box>
  );
}

export default LandingPage;
