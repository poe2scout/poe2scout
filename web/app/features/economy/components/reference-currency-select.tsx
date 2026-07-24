import type { LeagueCurrency } from "~/features/league/types";
import { getLeagueCurrencyIdentifier } from "~/features/league/currency-identifier";
import SelectField from "~/shared/components/select";

export default function ReferenceCurrencySelect({
  value,
  options,
  onChange,
}: {
  value: string;
  options: LeagueCurrency[];
  onChange: (value: string) => void;
}) {
  return (
    <SelectField
      label="Currency"
      value={value}
      onChange={(event) => onChange(event.currentTarget.value)}
      className="block min-w-48 text-sm text-white/80"
      wrapperClassName="h-10 bg-zinc-900/40 px-3 focus-within:bg-zinc-950/60"
    >
      {options.map((option) => {
        const identifier = getLeagueCurrencyIdentifier(option);
        return (
          <option key={identifier} value={identifier}>
            {option.text}
          </option>
        );
      })}
    </SelectField>
  );
}
