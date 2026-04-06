import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Category, CategoryResponse } from '../types';
import { fetchCategories as fetchCategoriesFromApi } from "../api/economy";
import { useLeague } from "./LeagueContext";

interface CategoryContextType {
  uniqueCategories: Category[];
  currencyCategories: Category[];
  loading: boolean;
}

const CategoryContext = createContext<CategoryContextType>({
  uniqueCategories: [],
  currencyCategories: [],
  loading: true,
});

export function CategoryProvider({ children }: { children: ReactNode }) {
  const [uniqueCategories, setUniqueCategories] = useState<Category[]>([]);
  const [currencyCategories, setCurrencyCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const { realm, league, loading: leagueLoading } = useLeague();
  const realmValue = realm?.value;

  useEffect(() => {
    if (leagueLoading || !realmValue || !league.value) {
      setUniqueCategories([]);
      setCurrencyCategories([]);
      setLoading(true);
      return;
    }

    let isMounted = true;

    const fetchCategories = async () => {
      setLoading(true);

      try {
        const data: CategoryResponse = await fetchCategoriesFromApi(league.value);

        if (!isMounted) {
          return;
        }

        setUniqueCategories(data.uniqueCategories);
        setCurrencyCategories(data.currencyCategories);
      } catch (error) {
        console.error('Error fetching categories:', error);
        if (!isMounted) {
          return;
        }

        setUniqueCategories([]);
        setCurrencyCategories([]);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchCategories();

    return () => {
      isMounted = false;
    };
  }, [league.value, leagueLoading, realmValue]);

  return (
    <CategoryContext.Provider value={{ uniqueCategories, currencyCategories, loading }}>
      {children}
    </CategoryContext.Provider>
  );
}

export const useCategories = () => useContext(CategoryContext); 
