import { useNavigate, useLocation } from "react-router-dom";
import { styled } from "@mui/material/styles";
import { CircularProgress, Drawer } from "@mui/material";
import { Typography } from "@mui/material";
import {
  CATEGORY_MAPPING,
} from "../constants";
import { useState } from "react";
import translations from "../translationskrmapping.json";
import { useLeague } from "../contexts/LeagueContext";
import { FormControl, Select, MenuItem, InputLabel } from "@mui/material";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from "@mui/material";
import { useCategories } from '../contexts/CategoryContext';
import { List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import { Circle } from "@mui/icons-material";

interface SideNavProps {
  isOpen: boolean;
  onClose: () => void;
  language?: "en" | "ko";
}

const Nav = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  borderRight: `1px solid ${theme.palette.divider}`,
  overflowY: "auto",
  display: "flex",
  flexDirection: "column",
  height: "100%",
  width: "230px",
  [theme.breakpoints.down("sm")]: {
    width: "100%",
  },
}));

const SectionTitle = styled(Typography)(({ theme }) => ({
  padding: "8px 16px",
  fontSize: "0.75rem",
  fontWeight: 700,
  color: theme.palette.text.secondary,
  backgroundColor: theme.palette.background.default,
  letterSpacing: "0.1em",
  borderBottom: `1px solid ${theme.palette.divider}`,
  marginTop: 0,
}));

const LeagueSelect = styled(Select)(() => ({
  ".MuiSelect-select": {
    padding: "4px 8px",
    fontSize: "0.9rem",
  },
  ".MuiOutlinedInput-notchedOutline": {
    borderColor: "rgba(255, 255, 255, 0.23)",
  },
  "&:hover .MuiOutlinedInput-notchedOutline": {
    borderColor: "rgba(255, 255, 255, 0.4)",
  },
}));

const LeagueContainer = styled("div")({
  padding: "8px 16px",
  borderBottom: "1px solid rgba(255, 255, 255, 0.12)",
});

function SideNav({ isOpen, onClose, language = "en" }: SideNavProps) {
  const { uniqueCategories, currencyCategories, loading } = useCategories();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = window.matchMedia("(max-width: 600px)").matches;
  const { league, setLeague, leagues } = useLeague();
  const [showWarningDialog, setShowWarningDialog] = useState(false);
  const [pendingLeague, setPendingLeague] = useState<string>("");

  const handleNavigation = (path: string) => {
    navigate(`/economy/${path}`);
    if (isMobile) {
      onClose();
    }
  };

  const getTranslatedText = (key: string) => {
    if (language === "ko" && key in translations) {
      return translations[key as keyof typeof translations];
    }
    return CATEGORY_MAPPING[key] || key;
  };

  const handleLeagueChange = (newLeagueValue: string) => {
    const newLeague = leagues.find(l => l.value === newLeagueValue);
    if (!newLeague) return;
    
    if (newLeague.value.toLowerCase().includes('hardcore')) {
      setPendingLeague(newLeagueValue);
      setShowWarningDialog(true);
    } else {
      setLeague(newLeague);
    }
  };

  const handleConfirmLeagueChange = () => {
    const newLeague = leagues.find(l => l.value === pendingLeague);
    if (newLeague) {
      setLeague(newLeague);
    }
    setShowWarningDialog(false);
  };

  if (loading) {
    return (
      <Nav style={{ justifyContent: 'center', alignItems: 'center' }}>
        <CircularProgress />
      </Nav>
    );
  }

  const content = (
    <Nav>
      <LeagueContainer>
        <FormControl size="small" fullWidth>
          <InputLabel id="league-select-label">
            {getTranslatedText("League")}
          </InputLabel>
          <LeagueSelect
            labelId="league-select-label"
            id="league-select"
            value={league.value}
            label="League"
            onChange={(e) => handleLeagueChange(e.target.value as string)}
          >
            {leagues.map((leagueOption) => (
              <MenuItem key={leagueOption.value} value={leagueOption.value}>
                {getTranslatedText(leagueOption.value)}
              </MenuItem>
            ))}
          </LeagueSelect>
        </FormControl>
      </LeagueContainer>

      <Dialog
        open={showWarningDialog}
        onClose={() => setShowWarningDialog(false)}
      >
        <DialogTitle>{language === "ko" ? "주의" : "Warning"}</DialogTitle>
        <DialogContent>
          {language === "ko"
            ? "하드코어 리그는 현재 개발 중입니다. 일부 기능이 제대로 작동하지 않을 수 있습니다."
            : "Hardcore league support is currently under development. Some features may not work as expected."}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowWarningDialog(false)}>
            {language === "ko" ? "취소" : "Cancel"}
          </Button>
          <Button onClick={handleConfirmLeagueChange} color="primary">
            {language === "ko" ? "계속하기" : "Continue"}
          </Button>
        </DialogActions>
      </Dialog>
      <List>
        <SectionTitle>Currency</SectionTitle>
        {currencyCategories.map((category) => (
          <ListItem key={category.apiId} disablePadding dense>
            <ListItemButton
              selected={location.pathname === `/economy/${category.apiId}`}
              onClick={() => handleNavigation(category.apiId)}
            >
              <ListItemIcon>
                {category.icon ? (
                  <img src={category.icon} alt={category.label} style={{ width: 24, height: 24 }} />
                ) : (
                  <Circle />
                )}
              </ListItemIcon>
              <ListItemText primary={category.label} />
            </ListItemButton>
          </ListItem>
        ))}

        <SectionTitle>Uniques</SectionTitle>
        {uniqueCategories.map((category) => (
          <ListItem key={category.apiId} disablePadding dense>
            <ListItemButton
              selected={location.pathname === `/economy/${category.apiId}`}
              onClick={() => handleNavigation(category.apiId)}
            >
              <ListItemIcon>
                {category.icon ? (
                  <img src={category.icon} alt={category.label} style={{ width: 24, height: 24 }} />
                ) : (
                  <Circle />
                )}
              </ListItemIcon>
              <ListItemText primary={category.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Nav>
  );

  return isMobile ? (
    <Drawer
      variant="temporary"
      open={isOpen}
      onClose={onClose}
      sx={{
        width: 280,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 280,
          boxSizing: 'border-box',
        },
      }}
    >
      {content}
    </Drawer>
  ) : (
    <div style={{ display: isOpen ? "block" : "none" }}>{content}</div>
  );
}

export default SideNav;
