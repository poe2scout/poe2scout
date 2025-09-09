import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { styled } from "@mui/material/styles";
import { Typography, IconButton, Tabs, Tab } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { useState } from "react";
import SideNav from "./ItemTypeSideNavbar";
import { useLanguage } from "../contexts/LanguageContext";
import translations from "../translationskrmapping.json";
import LeagueContainer from "./LeagueContainer";

const TopBar = styled("div")(({ theme }) => ({
  height: "50px",
  backgroundColor: theme.palette.background.paper,
  borderBottom: `1px solid ${theme.palette.divider}`,
  display: "flex",
  alignItems: "center",
  padding: "0 20px",
  justifyContent: "space-between",
}));

const MainContent = styled("div")({
  display: "flex",
  height: "calc(100vh - 50px)",
  overflow: "hidden",
});

const ContentArea = styled("div")<{ fullWidth?: boolean }>(() => ({
  flex: 1,
  overflow: "auto",
  display: "flex",
  flexDirection: "column",
  minHeight: 0,
}));

const MenuButton = styled(IconButton)(({ theme }) => ({
  display: "none",
  [theme.breakpoints.down("sm")]: {
    display: "block",
  },
}));

function Layout() {
  const [isSideNavOpen, setIsSideNavOpen] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const { language } = useLanguage();

  const currentTab =
    location.pathname === "/"
      ? ""
      : location.pathname.split("/")[1] || "";
  const showSideNav = currentTab === "economy";

  const handleTabChange = (newValue: string) => {
    navigate(`/${newValue}`);
  };

  return (
    <>
      <TopBar>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {showSideNav && (
            <MenuButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={() => setIsSideNavOpen(!isSideNavOpen)}
            >
              <MenuIcon />
            </MenuButton>
          )}
          <div
            onClick={() => navigate("/")}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              cursor: "pointer",
            }}
          >
            <img
              src="/favicon.ico"
              alt="poe2scout"
              style={{ width: "24px", height: "24px" }}
            />
            <Typography variant="h6">Poe2 Scout</Typography>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <LeagueContainer />

          <Tabs
            value={currentTab}
            onChange={(_, newValue) => handleTabChange(newValue)}
            sx={{
              minHeight: { xs: '40px', sm: '50px' },
              "& .MuiTab-root": {
                minHeight: { xs: '40px', sm: '50px' },
                px: { xs: 1, sm: 2 },
                fontSize: { xs: '0.8rem', sm: '1rem' },
                "&:focus": {
                  outline: "none !important",
                },
                "&.Mui-focusVisible": {
                  outline: "none !important",
                },
              },
              "& .Mui-focused": {
                outline: "none !important",
              },
            }}
          >
            <Tab
              label={language === "ko" ? translations["Economy"] : "Economy"}
              value="economy"
              disableRipple
            />
            <Tab
              label={"Currency Exchange"}
              value="exchange"
              disableRipple
            />
          </Tabs>
        </div>
      </TopBar>
      <MainContent>
        {showSideNav && (
          <SideNav
            isOpen={isSideNavOpen}
            onClose={() => setIsSideNavOpen(false)}
            language={language}
          />
        )}
        <ContentArea fullWidth={true}>
          <Outlet />
        </ContentArea>
      </MainContent>
    </>
  );
}

export default Layout;
