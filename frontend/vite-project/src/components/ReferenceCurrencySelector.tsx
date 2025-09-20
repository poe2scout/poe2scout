import React from "react";
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  SelectChangeEvent,
} from "@mui/material";


export type BaseCurrencies = "exalted" | "divine" | "chaos";
export const BaseCurrencyList: BaseCurrencies[] = ["exalted", "divine" , "chaos"];

interface ReferenceCurrencySelectorProps {
  currentReference: BaseCurrencies;
  options?: BaseCurrencies[];
  onReferenceChange: (newReference: BaseCurrencies) => void;
}

export const CurrencyNameMap: Record<BaseCurrencies, string> = {
  exalted: "Exalted Orb",
  divine: "Divine Orb",
  chaos: "Chaos Orb"
};

const ReferenceCurrencySelector: React.FC<ReferenceCurrencySelectorProps> = ({
  currentReference,
  onReferenceChange,
  options = BaseCurrencyList
}) => {
  const handlePresetChange = (event: SelectChangeEvent) => {
    const newSelection = event.target.value as BaseCurrencies;
    onReferenceChange(newSelection);
  };

  const labelId = "nominal-currency-select";

  return (
    <Stack direction="row" spacing={1} alignItems="center">
      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel id={labelId}>Nominal Currency</InputLabel>
        <Select
          labelId={labelId}
          value={currentReference}
          label="Nominal Currency"
          onChange={handlePresetChange}
        >
          {options.map((option) => (
            <MenuItem key={option} value={option}>
              {CurrencyNameMap[option]}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Stack>
  );
};

export default ReferenceCurrencySelector;
