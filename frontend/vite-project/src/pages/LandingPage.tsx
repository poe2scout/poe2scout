import { Typography, Button, Container, Box, Link } from "@mui/material";
import { styled } from "@mui/material/styles";
import { useNavigate } from "react-router-dom";
import market from "../assets/market.png";
import builds from "../assets/builds.png";

const HeroSection = styled("div")(({ theme }) => ({
  minHeight: "calc(100vh - 50px)",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  textAlign: "center",
  paddingTop: "0px",
  marginTop: "0px",
  gap: theme.spacing(4),
}));

const FeatureGrid = styled("div")(({ theme }) => ({
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
  gap: theme.spacing(4),
  marginTop: theme.spacing(8),
  marginBottom: theme.spacing(8),
}));

const FeatureCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
  border: `1px solid ${theme.palette.divider}`,
  transition: "transform 0.2s ease-in-out",
  "&:hover": {
    transform: "translateY(-4px)",
  },
}));

const Footer = styled("footer")(({ theme }) => ({
  borderTop: `1px solid ${theme.palette.divider}`,
  padding: theme.spacing(6),
  marginTop: "auto",
  backgroundColor: theme.palette.background.paper,
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

  return (
    <Container maxWidth="lg" sx={{ marginTop: "0px" }}>
      <HeroSection>
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center",
              gap: 2,
            }}
          >
            <Typography
              variant="h1"
              sx={{
                fontSize: "4rem",
                fontWeight: "light",
                letterSpacing: "0.2rem",
                mb: 2,
              }}
            >
              Poe2 Scout
            </Typography>
            <Typography variant="h5" color="textSecondary" sx={{ mb: 1 }}>
              Your Ultimate Path of Exile 2 Companion
            </Typography>
            <Typography
              variant="body1"
              color="textSecondary"
              sx={{
                maxWidth: "600px",
                mb: 4,
              }}
            >
              Track market prices, analyze build trends, and make informed
              decisions with up to date POE2 data
            </Typography>
          </Box>

          <Box sx={{ display: "flex", gap: 2 }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate("/economy/currency")}
            >
              MARKET
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate("/builds")}
            >
              BUILDS
            </Button>
          </Box>

          <Box
            sx={{
              display: "flex",
              gap: 8,
              justifyContent: "center",
              width: "100%",
              maxWidth: "1000px",
              margin: "2rem auto",
              px: 4,
            }}
          >
            <img
              src={market}
              alt="Currency Exchange"
              style={{
                width: "40%",
                objectFit: "contain",
                borderRadius: "8px",
                boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
              }}
            />
            <img
              src={builds}
              alt="Class Distribution"
              style={{
                width: "40%",
                objectFit: "contain",
                borderRadius: "8px",
                boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
              }}
            />
          </Box>
        </Box>
      </HeroSection>

      <FeatureGrid>
        <FeatureCard>
          <Typography variant="h6" gutterBottom>
            Real-time Prices
          </Typography>
          <Typography color="textSecondary">
            Stay updated with the latest market prices for all items in POE2
          </Typography>
        </FeatureCard>

        <FeatureCard>
          <Typography variant="h6" gutterBottom>
            Price History
          </Typography>
          <Typography color="textSecondary">
            Track price trends over time with our interactive charts
          </Typography>
        </FeatureCard>

        <FeatureCard>
          <Typography variant="h6" gutterBottom>
            Easy Trading
          </Typography>
          <Typography color="textSecondary">
            Direct links to the official trade site for quick transactions
          </Typography>
        </FeatureCard>
      </FeatureGrid>

      <Footer>
        <div className="footer-content">
          <div className="footer-section">
            <Typography variant="h6" gutterBottom>
              About
            </Typography>
            <Typography variant="body2" color="text.secondary">
              POE2 Scout is your go-to tool for price checking and market
              analysis in Path of Exile 2. We help you make informed trading
              decisions with real-time data and historical price tracking.
            </Typography>
          </div>
          <div className="footer-section">
            <Typography variant="h6" gutterBottom>
              Quick Links
            </Typography>
            <div className="footer-links">
              <Link href="/economy/currency" color="inherit">
                Currency Exchange
              </Link>
              <Link href="/economy/accessory" color="inherit">
                Unique Accessories
              </Link>
            </div>
          </div>
          <div className="footer-section">
            <Typography variant="h6" gutterBottom>
              Community
            </Typography>
            <div className="footer-links">
              <Link
                href="https://discord.gg/EHXVdQCpBq"
                color="inherit"
                target="_blank"
                rel="noopener noreferrer"
              >
                Discord
              </Link>
              <Typography color="inherit" sx={{ mt: 1 }}>
                Join the community on discord! For bug reports, feature requests
                and more.
              </Typography>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <Typography variant="body2">
            © {new Date().getFullYear()} Poe2 Scout. Not affiliated with
            Grinding Gear Games.
          </Typography>
        </div>
      </Footer>
    </Container>
  );
}

export default LandingPage;
