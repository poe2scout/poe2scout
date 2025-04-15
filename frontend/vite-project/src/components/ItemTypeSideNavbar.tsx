import { useNavigate, useLocation } from "react-router-dom";
import { styled } from "@mui/material/styles";
import { CircularProgress, Drawer } from "@mui/material";
import { Typography } from "@mui/material";
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





function SideNav({ isOpen, onClose }: SideNavProps) {
  const { uniqueCategories, currencyCategories, loading } = useCategories();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = window.matchMedia("(max-width: 600px)").matches;
  const handleNavigation = (path: string) => {
    navigate(`/economy/${path}`);
    if (isMobile) {
      onClose();
    }
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
