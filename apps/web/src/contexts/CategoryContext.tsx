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
  const { realm } = useLeague();

  useEffect(() => {
    if (!realm) {
      return;
    }

    const fetchCategories = async () => {
      setLoading(true);
      try {
        const data: CategoryResponse = await fetchCategoriesFromApi();
        setUniqueCategories(data.uniqueCategories);
        setCurrencyCategories(data.currencyCategories);
      } catch (error) {
        console.error('Error fetching categories:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, [realm?.value]);

  return (
    <CategoryContext.Provider value={{ uniqueCategories, currencyCategories, loading }}>
      {children}
    </CategoryContext.Provider>
  );
}

export const useCategories = () => useContext(CategoryContext); 
