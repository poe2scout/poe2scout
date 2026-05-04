import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useFetcher } from "react-router";
import getFiltersQueryOptions from "~/api/query-options/filters";

export default function ItemSearch({ realmId }: { realmId: string }) {
  const fetcher = useFetcher();
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  const { data, isPending } = useQuery(getFiltersQueryOptions(realmId));
  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setDebouncedSearch(search);
    }, 200);

    return () => window.clearTimeout(timeoutId);
  }, [search]);

  const suggestions = useMemo(() => {
    if (data == undefined) {
      return [];
    }

    const filters = data.filters;
    const query = debouncedSearch.trim().toLowerCase();

    if (!query) {
      return [];
    }

    return filters
      .filter(
        (filter) =>
          filter.displayName.toLowerCase().includes(query) ||
          filter.category.toLowerCase().includes(query),
      )
      .slice(0, 24);
  }, [data?.filters, debouncedSearch]);

  return (
    <fetcher.Form className="mx-auto mt-3" role="search">
      <label
        htmlFor="item-filter-search"
        className="mb-1.5 block text-sm text-white/80"
      >
        Search items
      </label>
      <div className="relative">
        <input
          id="item-filter-search"
          name="filter"
          type="search"
          value={search}
          onFocus={() => setIsFocused(true)}
          onBlur={() => window.setTimeout(() => setIsFocused(false), 100)}
          onChange={(event) => setSearch(event.currentTarget.value)}
          placeholder={isPending ? "Loading filters..." : "Search by item type"}
          disabled={isPending}
          className="h-10 w-full rounded-sm border border-secondary/35 bg-black/20 px-3 text-sm text-white transition outline-none placeholder:text-white/45 focus:border-secondary focus:bg-black/30 focus:ring-2 focus:ring-secondary/25 disabled:cursor-wait disabled:opacity-60"
          autoComplete="off"
        />
        {isFocused && suggestions.length > 0 && (
          <div className="absolute right-0 left-0 z-20 mt-1 max-h-[50vh] overflow-y-auto rounded-sm border border-secondary/35 bg-zinc-950 shadow-lg shadow-black/30">
            {suggestions.map((filter) => (
              <button
                key={filter.identifier}
                type="button"
                className="flex w-full flex-col px-3 py-2 text-left text-sm hover:bg-secondary/20 focus:bg-secondary/25 focus:outline-none"
                onClick={() => setSearch(filter.displayName)}
              >
                <span>{filter.displayName}</span>
                <span className="text-xs text-white/50">{filter.category}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </fetcher.Form>
  );
}
