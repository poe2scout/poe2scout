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

  return (
    <Stack direction="row" spacing={1} alignItems="center" sx={{paddingLeft: "20px"}}>
      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel id="period-select-label">Relative Currency</InputLabel>
        <Select
          labelId="relative-currency-select-label"
          value={currentReference}
          label="Relative Currency"
          onChange={handlePresetChange}
        >
          {options.map(option => {

            return (<MenuItem value={option}>
                {CurrencyNameMap[option]}
            </MenuItem>         )
          })}
        </Select>
      </FormControl>
    </Stack>
  );
};

export default ReferenceCurrencySelector;
