import type { UTCTimestamp } from "lightweight-charts";

export { default as formatInteger } from "~/shared/utils/format-number";

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
