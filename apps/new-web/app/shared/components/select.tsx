import type { ReactNode, SelectHTMLAttributes } from "react";

type SelectFieldProps = Omit<
  SelectHTMLAttributes<HTMLSelectElement>,
  "className"
> & {
  label?: ReactNode;
  labelClassName?: string;
  className?: string;
  wrapperClassName?: string;
  selectClassName?: string;
};

export default function SelectField({
  label,
  labelClassName = "mb-1.5 block",
  className = "block",
  wrapperClassName = "h-10 bg-zinc-900/40 px-3",
  selectClassName = "text-sm",
  children,
  ...selectProps
}: SelectFieldProps) {
  return (
    <label className={className}>
      {label !== undefined && <span className={labelClassName}>{label}</span>}
      <div
        className={`rounded-sm border border-secondary/35 transition focus-within:border-secondary focus-within:ring-2 focus-within:ring-secondary/25 ${wrapperClassName}`}
      >
        <select
          {...selectProps}
          className={`h-full w-full bg-transparent text-white outline-none ${selectClassName}`}
        >
          {children}
        </select>
      </div>
    </label>
  );
}
