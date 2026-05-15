import ItemDetail, { handle } from "./item-detail";
import type { Route } from "./+types/unique-item-detail";

export { handle };

export default function UniqueItemDetail({ params }: Route.ComponentProps) {
  return <ItemDetail params={params} />;
}
