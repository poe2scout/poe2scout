import { TextField, Popper, Paper, MenuItem, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useState, useRef, useEffect } from "react";

// Define the structure of the items in the searchable list
export interface SearchableItem {
  display_name: string;
  category: string;
  identifier: string;
}

interface SearchAutocompleteProps {
  onItemSelect: (category: string, identifier: string) => void;
  onClear: () => void;
  placeholder: string;
  initialValue?: string;
  searchableItems: SearchableItem[];
  isLoadingList?: boolean;
}

export function SearchAutocomplete({
  onItemSelect,
  onClear,
  placeholder,
  initialValue = "",
  searchableItems,
  isLoadingList = false,
}: SearchAutocompleteProps) {
  const [searchTerm, setSearchTerm] = useState(initialValue);
  const [isOpen, setIsOpen] = useState(false);
  const anchorEl = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const [filteredResults, setFilteredResults] = useState<SearchableItem[]>([]);
  const [activeIndex, setActiveIndex] = useState<number>(-1);

  useEffect(() => {
    setSearchTerm(initialValue);
    if (!initialValue) {
      setIsOpen(false);
    }
  }, [initialValue]);

  useEffect(() => {
    if (searchTerm && searchableItems.length > 0) {
      const lowerSearchTerm = searchTerm.toLowerCase();
      const results = searchableItems
        .filter((item) =>
          item.display_name.toLowerCase().includes(lowerSearchTerm)
        );
      setFilteredResults(results);
      setIsOpen(results.length > 0);
      setActiveIndex(-1);
    } else {
      setFilteredResults([]);
      setIsOpen(false);
    }
  }, [searchTerm, searchableItems]);

  useEffect(() => {
    if (isOpen && activeIndex >= 0 && listRef.current) {
      const activeItem = listRef.current.children[activeIndex] as HTMLElement;
      if (activeItem) {
        activeItem.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
        });
      }
    }
  }, [activeIndex, isOpen]);

  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
  };

  const handleClear = () => {
    setSearchTerm("");
    setFilteredResults([]);
    setIsOpen(false);
    onClear();
  };

  const handleItemClick = (item: SearchableItem) => {
    setIsOpen(false);
    onItemSelect(item.category, item.identifier);
  };  

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (!isOpen || filteredResults.length === 0) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setActiveIndex((prev) => (prev + 1) % filteredResults.length);
        break;
      case 'ArrowUp':
        event.preventDefault();
        setActiveIndex((prev) => (prev - 1 + filteredResults.length) % filteredResults.length);
        break;
      case 'Enter':
        if (activeIndex >= 0) {
          event.preventDefault();
          handleItemClick(filteredResults[activeIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        break;
      default:
        break;
    }
  };

  const isDisabled = isLoadingList || !!initialValue;
  const currentPlaceholder = placeholder;

  return (
    <div ref={anchorEl} style={{ position: "relative", width: "100%" }}>
      <TextField
        placeholder={currentPlaceholder}
        value={searchTerm}
        onChange={(e) => handleSearchChange(e.target.value)}
        onKeyDown={handleKeyDown}
        variant="outlined"
        size="small"
        fullWidth
        disabled={isDisabled}
        onFocus={() => {
          if (searchTerm && filteredResults.length > 0) {
            setIsOpen(true);
          }
        }}
        onBlur={() => {
          setTimeout(() => setIsOpen(false), 150);
        }}
        InputProps={{
          endAdornment: (initialValue || searchTerm) && (
            <IconButton size="small" onClick={handleClear} edge="end">
              <CloseIcon fontSize="small" />
            </IconButton>
          ),
        }}
        inputProps={{
          autoComplete: "off",
        }}
      />
      <Popper
        open={isOpen && filteredResults.length > 0 && !isDisabled}
        anchorEl={anchorEl.current}
        placement="bottom-start"
        style={{ width: anchorEl.current?.clientWidth, zIndex: 1300 }}
        onMouseEnter={() => setActiveIndex(-1)}
      >
        <Paper
          ref={listRef}
          component="div"
          sx={{ maxHeight: 300, overflowY: 'auto' }}
        >
          {filteredResults.map((item, index) => (
            <MenuItem
              key={item.identifier}
              selected={index === activeIndex}
              onMouseDown={() => handleItemClick(item)}
            >
              {item.display_name}
            </MenuItem>
          ))}
        </Paper>
      </Popper>
    </div>
  );
}
