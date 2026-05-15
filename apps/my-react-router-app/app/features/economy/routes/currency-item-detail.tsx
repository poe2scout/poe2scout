import ItemDetail, { handle } from "./item-detail";
import type { Route } from "./+types/currency-item-detail";

export { handle };

export default function CurrencyItemDetail({ params }: Route.ComponentProps) {
  return <ItemDetail params={params} />;
}
