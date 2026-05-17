import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import getFiltersQueryOptions, { type Filter } from "../queries/filters";

export default function ItemSearch({
  realmId,
  activeSearchValue,
  onFilterSelect,
  onSearchFilterRemove,
  endContent,
}: {
  realmId: string;
  activeSearchValue: string;
  onFilterSelect: (filter: Filter) => void;
  onSearchFilterRemove: () => void;
  endContent?: ReactNode;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  const { data, isPending } = useQuery(getFiltersQueryOptions(realmId));
  const activeSearchFilter = useMemo(() => {
    if (!activeSearchValue || data == undefined) {
      return null;
    }

    return (
      data.filters.find((filter) => filter.identifier === activeSearchValue) ??
      null
    );
  }, [activeSearchValue, data?.filters]);
  const activeSearchLabel =
    activeSearchFilter?.displayName ?? activeSearchValue;

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

  const selectFilter = (filter: Filter) => {
    setSearch("");
    setIsFocused(false);
    inputRef.current?.blur();
    onFilterSelect(filter);
  };

  return (
    <div className="mt-3 space-y-3">
      <div className="flex w-full flex-col gap-3 lg:w-auto lg:flex-row lg:items-end">
        <div className="w-full lg:max-w-xl" role="search">
          <label
            htmlFor="item-filter-search"
            className="mb-1.5 block text-sm text-white/80"
          >
            Search items
          </label>
          <div className="relative">
            <input
              ref={inputRef}
              id="item-filter-search"
              name="filter"
              type="search"
              value={search}
              onFocus={() => setIsFocused(true)}
              onBlur={() => window.setTimeout(() => setIsFocused(false), 100)}
              onChange={(event) => setSearch(event.currentTarget.value)}
              placeholder={
                isPending ? "Loading filters..." : "Search by item type"
              }
              disabled={isPending}
              className="h-10 w-full rounded-sm border border-secondary/35 bg-zinc-900/40 px-3 text-sm text-white transition outline-none placeholder:text-white/45 focus:border-secondary focus:bg-zinc-950/60 focus:ring-2 focus:ring-secondary/25 disabled:cursor-wait disabled:opacity-60"
              autoComplete="off"
            />
            {isFocused && suggestions.length > 0 && (
              <div className="absolute right-0 left-0 z-20 mt-1 max-h-[50vh] overflow-y-auto rounded-sm border border-secondary/35 bg-zinc-900 shadow-lg shadow-black/30">
                {suggestions.map((filter) => (
                  <button
                    key={filter.identifier}
                    type="button"
                    className="flex w-full flex-col px-3 py-2 text-left text-sm hover:bg-secondary/20 focus:bg-secondary/25 focus:outline-none"
                    onMouseDown={(event) => {
                      event.preventDefault();
                      selectFilter(filter);
                    }}
                  >
                    <span>{filter.displayName}</span>
                    <span className="text-xs text-white/50">
                      {filter.category}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        {endContent}
      </div>
      {activeSearchLabel && (
        <div className="flex flex-wrap gap-2">
          <span className="inline-flex max-w-full items-center gap-2 rounded-full border border-secondary/35 bg-secondary/15 px-3 py-1 text-sm text-white">
            <span className="min-w-0 truncate">
              <span className="text-white/55">search: </span>
              {activeSearchLabel}
            </span>
            <button
              type="button"
              className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-white/70 transition hover:bg-white/15 hover:text-white focus:bg-white/20 focus:text-white focus:outline-none"
              onClick={onSearchFilterRemove}
              aria-label={`Remove search filter ${activeSearchLabel}`}
            >
              x
            </button>
          </span>
        </div>
      )}
    </div>
  );
}
