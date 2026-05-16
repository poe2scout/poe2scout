import type { ReactNode } from "react";

export type TableColumn<T> = {
  id: string;
  header: ReactNode;
  className?: string;
  headerClassName?: string;
  cell: (row: T) => ReactNode;
};
