import React from "react";
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  SelectChangeEvent,
} from "@mui/material";

import { CurrencyMetaSource, getCurrencyLabel } from "../currencyMeta";

export type BaseCurrencies = string;
export const BaseCurrencyList: BaseCurrencies[] = ["exalted", "divine", "chaos"];

interface ReferenceCurrencySelectorProps {
  currentReference: BaseCurrencies;
  options?: BaseCurrencies[];
  onReferenceChange: (newReference: BaseCurrencies) => void;
  labelMap?: Record<string, string>;
  currencyMeta?: CurrencyMetaSource;
}

const ReferenceCurrencySelector: React.FC<ReferenceCurrencySelectorProps> = ({
  currentReference,
  onReferenceChange,
  options = BaseCurrencyList,
  labelMap,
  currencyMeta,
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
              {labelMap?.[option] ?? getCurrencyLabel(option, undefined, currencyMeta)}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Stack>
  );
};

export default ReferenceCurrencySelector;
