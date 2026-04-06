import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { ItemTable } from "../components/ItemTable";
import { Box } from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useCategories } from "../contexts/CategoryContext";
import { CircularProgress } from "@mui/material";
import { useLeague } from "../contexts/LeagueContext";
import AdSense from "../components/Banner";

export function EconomyPage() {
  const { type } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialSearch = searchParams.get("search");
  const [error, setError] = useState<string | null>(null);
  const {
    uniqueCategories,
    currencyCategories,
    loading: categoriesLoading,
  } = useCategories();
  const { language } = useLanguage();
  const {  loading: leagueLoading } = useLeague();
  const availableCategories = useMemo(
    () => [...currencyCategories, ...uniqueCategories],
    [currencyCategories, uniqueCategories],
  );
  const defaultCategory = availableCategories[0]?.apiId;
  const currentCategoryExists = type
    ? availableCategories.some((category) => category.apiId === type)
    : false;
  const itemType =
    (type && currentCategoryExists ? type : defaultCategory) || type || "currency";

  useEffect(() => {
    setError(null);
  }, [itemType]);

  useEffect(() => {
    if (categoriesLoading || leagueLoading || !type) {
      return;
    }

    if (!currentCategoryExists && defaultCategory) {
      navigate(`/economy/${defaultCategory}`, { replace: true });
    }
  }, [
    availableCategories,
    categoriesLoading,
    currentCategoryExists,
    defaultCategory,
    leagueLoading,
    navigate,
    type,
  ]);

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

  const pageContent = (
    <Box
      sx={{
        width: "100%",
        height: "100%",
        flexDirection: "column",
        gap: 2,
      }}
    >
      <Box>
        <AdSense format="horizontal"/>
      </Box>
      <Box sx={{ flexGrow: 1, minHeight: 0 }}>
        <ItemTable
          type={itemType}
          language={language}
          initialSearch={initialSearch || undefined}
        />
      </Box>
    </Box>
  );

  if (error) {
    return pageContent;
  }

  return pageContent;
}

export default EconomyPage;
