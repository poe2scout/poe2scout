import { useParams, useSearchParams } from "react-router-dom";
import { ItemTable } from "../components/ItemTable";
import { Box, IconButton, Snackbar } from "@mui/material";
import { useEffect, useState } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useCategories } from "../contexts/CategoryContext";
import { CircularProgress } from "@mui/material";
import { useLeague } from "../contexts/LeagueContext";
import CloseIcon from '@mui/icons-material/Close';

export function EconomyPage() {
  const { type } = useParams();
  const [searchParams] = useSearchParams();
  const initialSearch = searchParams.get("search");
  const [error, setError] = useState<string | null>(null);
  const { currencyCategories, loading: categoriesLoading } = useCategories();
  const { language } = useLanguage();
  const {  loading: leagueLoading } = useLeague();
  // If no type is provided, wait for categories to load to determine default
  const itemType = type || (currencyCategories[0]?.apiId || "currency");
  const [open, setOpen] = useState<boolean>(true);

  useEffect(() => {
    setError(null);
  }, [itemType]);

  if (categoriesLoading || leagueLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "85vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ width: "100%", height: "100%" }}>
      <ItemTable
        type={itemType}
        language={language}
        initialSearch={initialSearch || undefined}
      />
    </Box>
    );
  }

  return (
    <Box sx={{ width: "100%", height: "100%" }}>
      <Snackbar
        open={open}
        message="Price fetching paused. Will resume with the new league. Currency will now be fetched from the currency exchange api. Unique prices will be fetched from only buyout listings avoiding price fixers."
        onClose={() => setOpen(false)}
        action={<IconButton
              aria-label="close"
              color="inherit"
              sx={{ p: 0.5 }}
              onClick={() => setOpen(false)}
            >
              <CloseIcon />
            </IconButton>}
      />
      <ItemTable
        type={itemType}
        language={language}
        initialSearch={initialSearch || undefined}
      />
    </Box> 
  );
}

export default EconomyPage;
