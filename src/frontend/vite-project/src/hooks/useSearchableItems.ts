import { useState, useEffect } from 'react';
import type { SearchableItem } from '../components/SearchAutocomplete'; // Adjust path if needed

export function useSearchableItems() {
  const [searchableItems, setSearchableItems] = useState<SearchableItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchItems = async () => {
      setLoading(true);
      setError(null);
      try {

        const response = await fetch(`${import.meta.env.VITE_API_URL}/items/filters`);
        if (!response.ok) {
          throw new Error(`HTTP error fetching searchable items! status: ${response.status}`);
        }

        const data = await response.json();
        const formattedItems: SearchableItem[] = data.map((item: any) => ({
          display_name: item.display_name,
          category: item.category,
          identifier: item.identifier,
        }));
        setSearchableItems(formattedItems);
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