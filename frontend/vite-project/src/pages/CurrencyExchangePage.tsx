import { useParams, useSearchParams } from "react-router-dom";
import { ItemTable } from "../components/ItemTable";
import { Box } from "@mui/material";
import { useEffect, useState } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useCategories } from "../contexts/CategoryContext";
import { CircularProgress } from "@mui/material";
import { useLeague } from "../contexts/LeagueContext";

export function CurrencyExchangePage() {
  const { type } = useParams();
  const [error, setError] = useState<string | null>(null);
  const {  loading: leagueLoading } = useLeague();
  // If no type is provided, wait for categories to load to determine default



  return (
    <Box sx={{ width: "100%", height: "100%" }}>

    </Box> 
  );
}

export default CurrencyExchangePage;
