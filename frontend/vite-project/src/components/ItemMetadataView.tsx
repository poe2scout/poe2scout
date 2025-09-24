import { styled } from "@mui/material/styles";
import { Paper } from "@mui/material";
import { ItemMetadata, CurrencyMetadata } from "../types";
import { useState, useEffect, useRef } from "react";

const MetadataContainer = styled(Paper)({
  position: "absolute",
  zIndex: 1000,
  backgroundColor: "rgba(0, 0, 0, 0.95)",
  border: "1px solid #483F30",
  minWidth: "300px",
  maxWidth: "400px",
  fontSize: "14px",
  color: "#7f7f7f",
  padding: 0,
});

const ItemHeader = styled("div")<{ isCurrency?: boolean }>(
  ({ isCurrency }) => ({
    backgroundColor: isCurrency ? "#1a1a1a" : "#462d1b",
    padding: "4px 8px",
    marginBottom: "8px",
    color: isCurrency ? "#7f7f7f" : "#af6025",
    textAlign: "center",
    fontSize: "1.2em",
  })
);

const Section = styled("div")({
  marginBottom: "8px",
  position: "relative",
  padding: "0 5px",
  "& + &": {
    "&::before": {
      content: '""',
      position: "absolute",
      top: 0,
      left: "37.5%",
      right: "37.5%",
      height: "1px",
      backgroundColor: "#483F30",
    },
    paddingTop: "8px",
  },
});

const PropertyLine = styled("div")({
  display: "flex",
  justifyContent: "center",
  gap: "8px",
  color: "#7f7f7f",
});

const ModLine = styled("div")<{ color?: string }>(({ color = "#8888FF" }) => ({
  color: color,
  marginBottom: "2px",
  textAlign: "center",
}));

const DescriptionText = styled("div")({
  color: "#7f7f7f",
  marginTop: "8px",
  textAlign: "center",
});

interface ItemMetadataViewProps {
  metadata: ItemMetadata | CurrencyMetadata;
  anchorEl: HTMLElement | null;
}

export function ItemMetadataView({
  metadata,
  anchorEl
}: ItemMetadataViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ top: 0, left: 0, transform: "" });

  useEffect(() => {
    if (!metadata || !anchorEl || !containerRef.current) return;

    const updatePosition = () => {
      const rect = anchorEl.getBoundingClientRect();
      const tooltipRect = containerRef.current?.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      if (!tooltipRect) return;

      // Horizontal positioning
      let left = rect.left + 150;
      if (left + tooltipRect.width > viewportWidth) {
        left = rect.left - tooltipRect.width - 20;
      }
      left = Math.max(
        10,
        Math.min(left, viewportWidth - tooltipRect.width - 10)
      );

      // Vertical positioning
      let top = rect.bottom + 5;
      let transform = "";

      // If tooltip would overflow bottom
      if (top + tooltipRect.height > viewportHeight) {
        top = rect.top - 5;
        transform = "translateY(-100%)";
      }

      // If tooltip would overflow top after flipping
      if (top + (transform ? -tooltipRect.height : 0) < 0) {
        top = 10;
        transform = "";
      }

      setPosition({ top, left, transform });
    };

    // Initial position update
    updatePosition();

    // Set up resize observer
    const resizeObserver = new ResizeObserver(updatePosition);
    resizeObserver.observe(containerRef.current);

    // Update position on scroll and resize
    window.addEventListener("scroll", updatePosition);
    window.addEventListener("resize", updatePosition);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener("scroll", updatePosition);
      window.removeEventListener("resize", updatePosition);
    };
  }, [metadata, anchorEl]);

  if (!metadata || !anchorEl) return null;

  if (
    !("stack_size" in metadata) &&
    metadata.properties?.["Jewel"] !== undefined
  ) {
    return null;
  }

  const isCurrency = "stack_size" in metadata;

  return (
    <MetadataContainer
      ref={containerRef}
      style={{
        position: "fixed",
        top: position.top,
        left: position.left,
        transform: position.transform,
        height: "auto",
        maxHeight: "80vh",
        overflowY: "auto",
        padding: 0,
      }}
    >
      <ItemHeader isCurrency={isCurrency}>{metadata.name}</ItemHeader>

      {/* Stack Size for Currency */}
      {isCurrency && (
        <Section>
          <PropertyLine>
            <span>{`Stack Size: ${metadata.stack_size}/${metadata.max_stack_size}`}</span>
          </PropertyLine>
        </Section>
      )}

      {/* Properties for Items */}
      {!isCurrency &&
        metadata.properties &&
        Object.keys(metadata.properties).length > 0 && (
          <Section>
            {Object.entries(metadata.properties).map(([key, value]) => (
              <PropertyLine key={key}>
                <span>{value !== null ? `${key}: ${value}` : key}</span>
              </PropertyLine>
            ))}
          </Section>
        )}

      {/* Requirements for Items */}
      {!isCurrency &&
        metadata.requirements &&
        Object.keys(metadata.requirements).length > 0 && (
          <Section>
            {Object.entries(metadata.requirements).map(([key, value]) => (
              <PropertyLine key={key}>
                <span>{`Requires ${key}: ${String(value)}`}</span>
              </PropertyLine>
            ))}
          </Section>
        )}

      {/* Effect for Currency / Implicit Mods for Items */}
      {isCurrency
        ? metadata.effect &&
          metadata.effect.length > 0 && (
            <Section>
              {metadata.effect.map((effect: string, index: number) => (
                <ModLine key={index} color="#8888FF">
                  {effect}
                </ModLine>
              ))}
            </Section>
          )
        : metadata.implicit_mods?.length > 0 && (
            <Section>
              {metadata.implicit_mods.map((mod: string, index: number) => (
                <ModLine key={index} color="#8888FF">
                  {mod}
                </ModLine>
              ))}
            </Section>
          )}

      {/* Explicit Mods for Items */}
      {!isCurrency && metadata.explicit_mods?.length > 0 && (
        <Section>
          {metadata.explicit_mods.map((mod: string, index: number) => (
            <ModLine key={index} color="#8888FF">
              {mod}
            </ModLine>
          ))}
        </Section>
      )}

      {/* Flavor Text */}
      {!isCurrency && metadata.flavor_text && (
        <Section>
          <ModLine
            color="#af6025"
            style={{ fontStyle: "italic", whiteSpace: "pre-wrap" }}
          >
            {metadata.flavor_text}
          </ModLine>
        </Section>
      )}

      {/* Description */}
      {metadata.description && (
        <Section>
          <DescriptionText style={{ whiteSpace: "pre-wrap", color: "#7f7f7f" }}>
            {metadata.description}
          </DescriptionText>
        </Section>
      )}
    </MetadataContainer>
  );
}
