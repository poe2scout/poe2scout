import { useMemo } from "react";
import type { ReactNode } from "react";
import { useNavigate, useSearchParams } from "react-router";
import type {
  ExchangeOrder,
  ExchangeSnapshotPair,
  ExchangeSort,
  ExchangeTableState,
} from "../types";

const ROWS_PER_PAGE_OPTIONS = [10, 25, 50, 100];

export default function ExchangePairTable({
  pairs,
  tableState,
  isLoading = false,
  isError = false,
}: {
  pairs: ExchangeSnapshotPair[];
  tableState: ExchangeTableState;
  isLoading?: boolean;
  isError?: boolean;
}) {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const filteredPairs = useMemo(() => {
    const search = tableState.search.trim().toLowerCase();

    if (!search) {
      return pairs;
    }

    return pairs.filter((pair) => getPairSearchText(pair).includes(search));
  }, [pairs, tableState.search]);

  const sortedPairs = useMemo(() => {
    return [...filteredPairs].sort((a, b) => {
      const compare =
        tableState.sort === "pair"
          ? getPairName(a).localeCompare(getPairName(b))
          : a.volume - b.volume;

      return tableState.order === "desc" ? -compare : compare;
    });
  }, [filteredPairs, tableState.order, tableState.sort]);

  const totalPages = Math.max(
    Math.ceil(sortedPairs.length / tableState.perPage),
    1,
  );
  const currentPage = Math.min(tableState.page, totalPages);
  const visiblePairs = sortedPairs.slice(
    (currentPage - 1) * tableState.perPage,
    currentPage * tableState.perPage,
  );

  const updateTableState = (patch: Partial<ExchangeTableState>) => {
    const nextState = { ...tableState, ...patch };
    const nextSearchParams = new URLSearchParams(searchParams);

    nextSearchParams.set("search", nextState.search);
    nextSearchParams.set("sort", nextState.sort);
    nextSearchParams.set("order", nextState.order);
    nextSearchParams.set("page", String(nextState.page));
    nextSearchParams.set("perPage", String(nextState.perPage));

    setSearchParams(nextSearchParams, { preventScrollReset: true });
  };

  const toggleSort = (sort: ExchangeSort) => {
    const order: ExchangeOrder =
      tableState.sort === sort && tableState.order === "asc" ? "desc" : "asc";

    updateTableState({ sort, order, page: 1 });
  };

  const openPair = (pair: ExchangeSnapshotPair) => {
    const query = searchParams.toString();
    navigate(
      `pair/${pair.currencyOne.itemId}/${pair.currencyTwo.itemId}${query ? `?${query}` : ""}`,
      { state: { pair, fromExchangeTable: true } },
    );
  };

  return (
    <section className="rounded-sm border border-secondary/35 bg-zinc-900 shadow-lg shadow-black/30">
      <div className="flex flex-col gap-3 border-b border-secondary/25 p-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">Trading Pairs</h2>
          <p className="text-sm text-white/55">
            {isLoading
              ? "Loading current pairs..."
              : `${filteredPairs.length.toLocaleString()} current pairs`}
          </p>
        </div>
        <label className="relative block w-full sm:w-80">
          <span className="sr-only">Search trading pairs</span>
          <input
            value={tableState.search}
            onChange={(event) =>
              updateTableState({ search: event.currentTarget.value, page: 1 })
            }
            placeholder="Search trading pairs"
            className="h-9 w-full rounded-sm border border-secondary/35 bg-zinc-950/60 px-3 pr-9 text-sm text-white transition outline-none placeholder:text-white/35 focus:border-secondary focus:ring-2 focus:ring-secondary/25"
          />
          {tableState.search && (
            <button
              type="button"
              aria-label="Clear trading pair search"
              onClick={() => updateTableState({ search: "", page: 1 })}
              className="absolute top-1 right-1 h-7 w-7 rounded-sm text-white/55 transition hover:bg-white/10 hover:text-white"
            >
              x
            </button>
          )}
        </label>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full table-fixed text-left text-sm text-white">
          <thead className="sticky top-0 z-10 bg-zinc-900 text-xs tracking-wide text-white/60 uppercase">
            <tr>
              <th className="w-2/5 border-b border-secondary/25 px-3 py-2 font-medium">
                <SortButton
                  active={tableState.sort === "pair"}
                  order={tableState.order}
                  onClick={() => toggleSort("pair")}
                >
                  Trading Pair
                </SortButton>
              </th>
              <th className="w-2/5 border-b border-secondary/25 px-3 py-2 text-right font-medium">
                Exchange Rate
              </th>
              <th className="w-1/5 border-b border-secondary/25 px-3 py-2 text-right font-medium">
                <SortButton
                  active={tableState.sort === "volume"}
                  order={tableState.order}
                  onClick={() => toggleSort("volume")}
                >
                  Volume
                </SortButton>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {isLoading ? (
              <tr>
                <td
                  colSpan={3}
                  className="px-3 py-12 text-center text-white/60"
                >
                  Loading trading pairs...
                </td>
              </tr>
            ) : isError ? (
              <tr>
                <td
                  colSpan={3}
                  className="px-3 py-12 text-center text-white/60"
                >
                  Failed to load trading pairs.
                </td>
              </tr>
            ) : visiblePairs.length > 0 ? (
              visiblePairs.map((pair) => (
                <tr
                  key={pair.currencyExchangeSnapshotPairId}
                  tabIndex={0}
                  onClick={() => openPair(pair)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      openPair(pair);
                    }
                  }}
                  className="cursor-pointer transition hover:bg-secondary/10 focus:bg-secondary/15 focus:outline-none"
                >
                  <td className="px-3 py-2 align-middle">
                    <PairName pair={pair} />
                  </td>
                  <td className="px-3 py-2 text-right align-middle">
                    <PairRate pair={pair} />
                  </td>
                  <td className="px-3 py-2 text-right align-middle text-white/80">
                    {pair.volume.toLocaleString(undefined, {
                      maximumFractionDigits: 0,
                    })}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={3}
                  className="px-3 py-12 text-center text-white/60"
                >
                  No trading pairs match your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="flex flex-col gap-3 border-t border-secondary/25 px-3 py-2 text-sm text-white/70 sm:flex-row sm:items-center sm:justify-between">
        <div>
          {isLoading
            ? "Loading pairs"
            : `Page ${currentPage.toLocaleString()} of ${totalPages.toLocaleString()} | ${filteredPairs.length.toLocaleString()} pairs`}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="flex items-center gap-2">
            <span>Rows</span>
            <select
              value={tableState.perPage}
              onChange={(event) =>
                updateTableState({
                  page: 1,
                  perPage: Number(event.currentTarget.value),
                })
              }
              className="h-8 rounded-sm border border-secondary/35 bg-zinc-950/60 px-2 text-white outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/25"
            >
              {ROWS_PER_PAGE_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={() => updateTableState({ page: currentPage - 1 })}
            disabled={isLoading || isError || currentPage <= 1}
            className="h-8 rounded-sm border border-secondary/35 px-3 text-white transition hover:bg-secondary/20 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
          >
            Previous
          </button>
          <button
            type="button"
            onClick={() => updateTableState({ page: currentPage + 1 })}
            disabled={isLoading || isError || currentPage >= totalPages}
            className="h-8 rounded-sm border border-secondary/35 px-3 text-white transition hover:bg-secondary/20 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
          >
            Next
          </button>
        </div>
      </div>
    </section>
  );
}

function SortButton({
  children,
  active,
  order,
  onClick,
}: {
  children: ReactNode;
  active: boolean;
  order: ExchangeOrder;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-1 text-inherit transition hover:text-white"
    >
      <span>{children}</span>
      <span className={active ? "text-secondary" : "text-white/25"}>
        {active ? (order === "asc" ? "asc" : "desc") : "sort"}
      </span>
    </button>
  );
}

function PairName({ pair }: { pair: ExchangeSnapshotPair }) {
  return (
    <div className="flex min-w-0 flex-wrap items-center gap-2">
      <CurrencyName item={pair.currencyOne} />
      <span className="text-white/35">/</span>
      <CurrencyName item={pair.currencyTwo} />
    </div>
  );
}

function CurrencyName({ item }: { item: ExchangeSnapshotPair["currencyOne"] }) {
  return (
    <span className="inline-flex min-w-0 items-center gap-1.5">
      {item.iconUrl && (
        <img src={item.iconUrl} alt="" className="h-7 w-7 object-contain" />
      )}
      <span className="truncate">{item.text}</span>
    </span>
  );
}

function PairRate({ pair }: { pair: ExchangeSnapshotPair }) {
  return (
    <div
      className="flex flex-wrap items-center justify-end gap-1.5"
      title={`1 ${pair.currencyOne.text} = ${formatPrice(
        pair.currencyOneData.pairPrice,
      )} ${pair.currencyTwo.text}`}
    >
      <RateValue value={1} iconUrl={pair.currencyOne.iconUrl} />
      <span className="text-white/35">=</span>
      <RateValue
        value={pair.currencyOneData.pairPrice}
        iconUrl={pair.currencyTwo.iconUrl}
      />
    </div>
  );
}

function RateValue({
  value,
  iconUrl,
}: {
  value: number;
  iconUrl: string | null;
}) {
  return (
    <span className="inline-flex items-center gap-1">
      <span>{formatPrice(value)}</span>
      {iconUrl && (
        <img src={iconUrl} alt="" className="h-5 w-5 object-contain" />
      )}
    </span>
  );
}

function getPairName(pair: ExchangeSnapshotPair) {
  return `${pair.currencyOne.text}/${pair.currencyTwo.text}`;
}

function getPairSearchText(pair: ExchangeSnapshotPair) {
  return [
    pair.currencyOne.text,
    pair.currencyTwo.text,
    pair.currencyOne.apiId,
    pair.currencyTwo.apiId,
    `${pair.currencyOne.text}/${pair.currencyTwo.text}`,
    `${pair.currencyOne.text} / ${pair.currencyTwo.text}`,
    `${pair.currencyOne.apiId}/${pair.currencyTwo.apiId}`,
    `${pair.currencyOne.apiId} / ${pair.currencyTwo.apiId}`,
  ]
    .join(" ")
    .toLowerCase();
}

function formatPrice(value: number) {
  return value.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
}
