import { useState, useEffect } from 'react';
import type { SearchableItem } from '../types';
import { fetchSearchableItems as fetchSearchableItemsFromApi } from "../api/economy";

export function useSearchableItems() {
  const [searchableItems, setSearchableItems] = useState<SearchableItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchItems = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchSearchableItemsFromApi();
        setSearchableItems(data);
      } catch (err) {
        console.error("Failed to fetch searchable items:", err);
        setError(err instanceof Error ? err.message : "An unknown error occurred");
        setSearchableItems([]); 
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, []); 

  return { searchableItems, loading, error };
}
