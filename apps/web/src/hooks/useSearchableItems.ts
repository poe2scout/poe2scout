import { useState, useEffect } from 'react';
import type { SearchableItem } from '../types';
import { fetchSearchableItems as fetchSearchableItemsFromApi } from "../api/economy";
import { useLeague } from "../contexts/LeagueContext";

export function useSearchableItems() {
  const [searchableItems, setSearchableItems] = useState<SearchableItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { realm } = useLeague();

  useEffect(() => {
    if (!realm) {
      return;
    }

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
  }, [realm?.value]); 

  return { searchableItems, loading, error };
}
