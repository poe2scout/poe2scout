import React, { useState, useEffect, useCallback } from "react";
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  TextField,
  Button,
  SelectChangeEvent, 
} from "@mui/material";

const LOGS_PER_DAY = 4;

type Selection = "week" | "month" | "threeMonths" | "all" | "custom";
type Unit = "days" | "weeks" | "months";

interface PeriodSelectorProps {
  currentLogCount: number;
  onLogCountChange: (newCount: number) => void;
  language: "en" | "ko";
  translations: { [key: string]: string };
}

const PRESET_VALUES: Record<Exclude<Selection, "custom">, number> = {
  week: 7 * LOGS_PER_DAY,
  month: 28 * LOGS_PER_DAY,     
  threeMonths: 84 * LOGS_PER_DAY,
  all: 168 * LOGS_PER_DAY, 
};

const valueToSelection = (value: number): Selection => {
  for (const [key, val] of Object.entries(PRESET_VALUES)) {
    if (val === value) {
      return key as Selection;
    }
  }
  return "custom"; 
};

const PeriodSelector: React.FC<PeriodSelectorProps> = ({
  currentLogCount,
  onLogCountChange,
  language,
  translations,
}) => {
  const [selection, setSelection] = useState<Selection>(() =>
    valueToSelection(currentLogCount)
  );

  const [customAmount, setCustomAmount] = useState<string>("10");
  const [customUnit, setCustomUnit] = useState<Unit>("days");

  useEffect(() => {
    setSelection(valueToSelection(currentLogCount));
  }, [currentLogCount]);

  const handlePresetChange = (event: SelectChangeEvent) => {
    const newSelection = event.target.value as Selection;
    setSelection(newSelection);
    if (newSelection !== "custom") {
      onLogCountChange(PRESET_VALUES[newSelection]);
    }
  };

  const handleApplyCustom = useCallback(() => {
    let days = 0;
    const amount = parseInt(customAmount, 10);
    if (isNaN(amount) || amount <= 0) {
      return;
    }

    switch (customUnit) {
      case "days":
        days = amount;
        break;
      case "weeks":
        days = amount * 7;
        break;
      case "months":
        days = amount * 30; 
        break;
      default:
        return;
    }
    
    const newLogCount = days * LOGS_PER_DAY;
    onLogCountChange(newLogCount);
  }, [customAmount, customUnit, onLogCountChange]);

  return (
    <Stack direction="row" spacing={1} alignItems="center">
      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel id="period-select-label">Period</InputLabel>
        <Select
          labelId="period-select-label"
          value={selection}
          label="Period"
          onChange={handlePresetChange}
        >
          <MenuItem value="week">
            {language === "ko" ? translations["Week"] : "Week"}
          </MenuItem>
          <MenuItem value="month">
            {language === "ko" ? translations["Month"] : "Month"}
          </MenuItem>
          <MenuItem value="threeMonths">
            {language === "ko" ? translations["3 Months"] : "3 Months"}
          </MenuItem>
          <MenuItem value="all">All</MenuItem>
          <MenuItem value="custom">
            {language === "ko" ? translations["Custom..."] : "Custom..."}
          </MenuItem>
        </Select>
      </FormControl>

      {selection === "custom" && (
        <>
          <TextField
            size="small"
            type="number"
            value={customAmount}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setCustomAmount(e.target.value)
            }
            sx={{ width: 80 }}
            InputProps={{ inputProps: { min: 1 } }}
          />
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <InputLabel id="unit-select-label">Unit</InputLabel>
            <Select
              labelId="unit-select-label"
              value={customUnit}
              label="Unit"
              onChange={(e: SelectChangeEvent) =>
                setCustomUnit(e.target.value as Unit)
              }
            >
              <MenuItem value="days">Days</MenuItem>
              <MenuItem value="weeks">Weeks</MenuItem>
              <MenuItem value="months">Months</MenuItem>
            </Select>
          </FormControl>
          <Button variant="contained" size="medium" onClick={handleApplyCustom}>
            {language === "ko" ? translations["Set"] : "Set"}
          </Button>
        </>
      )}
    </Stack>
  );
};

export default PeriodSelector;