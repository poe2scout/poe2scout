import { styled } from "@mui/material/styles";
import { useRef, useState } from "react";
import { ItemMetadataView } from "../ItemMetadataView";
import { ItemMetadata, CurrencyMetadata } from "../../types";

interface ItemNameProps {
  iconUrl: string | null;
  name: string;
  isUnique: boolean;
  itemMetadata: ItemMetadata | CurrencyMetadata | null;
  iconPostFixed?: boolean;
}
const ItemIcon = styled("img")({
  width: "32px",
  height: "32px",
  objectFit: "contain",
  flexShrink: 0,
});
const ItemNameContainer = styled("div")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: "6px",
  fontSize: "0.9em",
  minWidth: 0,
  "& .name-type-container": {
    minWidth: 0,
    overflow: "hidden",
    whiteSpace: "nowrap",
    textOverflow: "ellipsis",
  },
  "& .type": {
    color: "#888",
    fontSize: "0.9em",
  },
  [theme.breakpoints.down("sm")]: {
    "& .type": {
      display: "none",
    },
    gap: "8px",
  },
}));

export function ItemName({
  iconUrl,
  name,
  isUnique,
  itemMetadata,
  iconPostFixed = false
}: ItemNameProps) {
  const displayName = name;
  const [showMetadata, setShowMetadata] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const imageSrc = iconUrl ? iconUrl : "/img/placeholder-icon.png";

  
  return (
      <ItemNameContainer
        ref={containerRef}
        onMouseEnter={() => setShowMetadata(true)}
        onMouseLeave={() => setShowMetadata(false)}
      >
        {!iconPostFixed && (
          <ItemIcon src={imageSrc} alt={displayName} />
        )}
        <div className="name-type-container">
          <span
            style={{ color: isUnique ? "#af6025" : "inherit", fontSize: "1.1em" }}
          >
            {displayName}
          </span>
          {(isUnique && itemMetadata) && (
            <span className="type">
              {"base_type" in itemMetadata
                ? ` ${itemMetadata.base_type}`
                : ` ${itemMetadata.name}`}
            </span>
          )}
        </div>
        {iconPostFixed && (
          <ItemIcon src={imageSrc} alt={displayName} />
        )}
        {showMetadata && itemMetadata && (
          <ItemMetadataView
            metadata={itemMetadata}
            anchorEl={containerRef.current}
          />
        )}
      </ItemNameContainer>
    );
  }
