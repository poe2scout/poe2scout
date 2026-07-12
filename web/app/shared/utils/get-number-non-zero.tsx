export default function getNumberNonZero(value: string | null): number | null {
  const parsedValue = Number(value);
  return parsedValue !== 0 ? parsedValue : null;
}
