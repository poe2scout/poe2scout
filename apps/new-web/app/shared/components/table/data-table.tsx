import type { ReactNode } from "react";
import type { TableColumn } from "./types";

export default function DataTable<T>({
  rows,
  columns,
  getRowKey,
  emptyContent = "No results found.",
  loadingContent,
  errorContent,
  footer,
  onRowClick,
}: {
  rows: T[];
  columns: TableColumn<T>[];
  getRowKey?: (row: T, index: number) => string | number;
  emptyContent?: ReactNode;
  loadingContent?: ReactNode;
  errorContent?: ReactNode;
  footer?: ReactNode;
  onRowClick?: (row: T) => void;
}) {
  const hasMessage = loadingContent || errorContent || rows.length === 0;
  const message = loadingContent ?? errorContent ?? emptyContent;

  return (
    <div className="overflow-hidden rounded-sm border border-secondary/35 bg-zinc-900 shadow-lg shadow-black/30">
      <div className="overflow-x-auto">
        <table className="min-w-full table-fixed text-left text-sm text-white">
          <thead className="sticky top-0 z-10 bg-zinc-900 text-xs tracking-wide text-white/60 uppercase">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.id}
                  scope="col"
                  className={`border-b border-secondary/25 px-3 py-2 font-medium ${column.headerClassName ?? column.className ?? ""}`}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {hasMessage ? (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-3 py-12 text-center text-white/60"
                >
                  {message}
                </td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr
                  key={getRowKey ? getRowKey(row, index) : index}
                  tabIndex={onRowClick ? 0 : undefined}
                  role={onRowClick ? "button" : undefined}
                  onClick={onRowClick ? () => onRowClick(row) : undefined}
                  onKeyDown={
                    onRowClick
                      ? (event) => {
                          if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault();
                            onRowClick(row);
                          }
                        }
                      : undefined
                  }
                  className={`transition hover:bg-secondary/10 ${onRowClick ? "cursor-pointer focus:bg-secondary/15 focus:outline-none" : ""}`}
                >
                  {columns.map((column) => (
                    <td
                      key={column.id}
                      className={`px-3 py-2 align-middle ${column.className ?? ""}`}
                    >
                      {column.cell(row)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {footer && <div className="border-t border-secondary/25">{footer}</div>}
    </div>
  );
}
