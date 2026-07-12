import DataTable from "~/shared/components/table/data-table";
import SelectField from "~/shared/components/select";
import type { TableColumn } from "~/shared/components/table/types";
import { getEconomyItemKey } from "./economy-table-columns";
import type { EconomyItem } from "../types";

export default function EconomyTable({
  items,
  columns,
  page,
  rowsPerPage,
  pages,
  totalItems,
  onPaginationChange,
  rowsPerPageOptions,
}: {
  items: EconomyItem[];
  columns: TableColumn<EconomyItem>[];
  page: number;
  rowsPerPage: number;
  pages: number;
  totalItems: number;
  onPaginationChange: (page: number, perPage: number) => void;
  rowsPerPageOptions: number[];
}) {
  const currentPage = page;
  const totalPages = Math.max(pages, 1);

  return (
    <DataTable
      rows={items}
      columns={columns}
      getRowKey={getEconomyItemKey}
      emptyContent="No items found for this category."
      footer={
        <div className="flex flex-col gap-3 px-3 py-2 text-sm text-white/70 sm:flex-row sm:items-center sm:justify-between">
          <div>
            Page {currentPage.toLocaleString()} of {totalPages.toLocaleString()}{" "}
            · {totalItems.toLocaleString()} items
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <SelectField
              label="Rows"
              value={rowsPerPage}
              onChange={(e) =>
                onPaginationChange(1, Number(e.currentTarget.value))
              }
              className="flex items-center gap-2"
              labelClassName=""
              wrapperClassName="h-8 bg-zinc-900/60 px-2"
              selectClassName="text-sm"
            >
              {rowsPerPageOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </SelectField>
            <button
              type="button"
              onClick={() => onPaginationChange(currentPage - 1, rowsPerPage)}
              disabled={currentPage <= 1}
              className="h-8 rounded-sm border border-secondary/35 px-3 text-white transition hover:bg-secondary/20 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
            >
              Previous
            </button>
            <button
              type="button"
              onClick={() => onPaginationChange(currentPage + 1, rowsPerPage)}
              disabled={currentPage >= totalPages}
              className="h-8 rounded-sm border border-secondary/35 px-3 text-white transition hover:bg-secondary/20 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
            >
              Next
            </button>
          </div>
        </div>
      }
    />
  );
}
