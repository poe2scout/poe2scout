import type { UTCTimestamp } from "lightweight-charts";
import type { EconomyItem } from "./types";

export { default as formatInteger } from "~/shared/utils/format-number";

export function getEconomyItemRouteSegment(item: EconomyItem) {
  const name = getEconomyItemDisplayName(item);
  const slug = name.trim().replace(/\s+/g, "-");

  return slug
    ? `${item.itemId}/${encodeURIComponent(slug)}`
    : String(item.itemId);
}

function getEconomyItemDisplayName(item: EconomyItem) {
  return "uniqueItemId" in item ? item.name : item.text;
}

export function toEpoch(time: string): UTCTimestamp {
  const date = time.endsWith("Z") ? time : `${time}Z`;
  return Math.floor(new Date(date).getTime() / 1000) as UTCTimestamp;
}

export function formatEpoch(time: UTCTimestamp) {
  return new Date(time * 1000).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatFixed(value: number) {
  return value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}
