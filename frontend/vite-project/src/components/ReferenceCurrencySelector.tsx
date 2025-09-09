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
export const BaseCurrencyList: string[] = ["exalted", "divine" , "chaos"];

interface ReferenceCurrencySelectorProps {
  currentReference: BaseCurrencies;
  onReferenceChange: (newReference: BaseCurrencies) => void;
}

const ReferenceCurrencySelector: React.FC<ReferenceCurrencySelectorProps> = ({
  currentReference,
  onReferenceChange
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
            <MenuItem value="exalted">
                {"Exalted orbs"}
            </MenuItem>            
            <MenuItem value="chaos">
                {"Chaos orbs"}
            </MenuItem>
            <MenuItem value="divine">
                {"Divine orbs"}
            </MenuItem>
        </Select>
      </FormControl>
    </Stack>
  );
};

export default ReferenceCurrencySelector;
