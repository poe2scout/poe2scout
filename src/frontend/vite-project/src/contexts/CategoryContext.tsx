import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Category, CategoryResponse } from '../types';

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

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/items/categories`);
        const data: CategoryResponse = await response.json();
        setUniqueCategories(data.unique_categories);
        setCurrencyCategories(data.currency_categories);
      } catch (error) {
        console.error('Error fetching categories:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return (
    <CategoryContext.Provider value={{ uniqueCategories, currencyCategories, loading }}>
      {children}
    </CategoryContext.Provider>
  );
}

export const useCategories = () => useContext(CategoryContext); 