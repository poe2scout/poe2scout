import { useQuery } from "@tanstack/react-query";
import getCurrencyItemsQueryOptions from "~/api/query-options/currency-items";

export default function ItemTable({
  realmId,
  leagueId,
  category,
  referenceCurrency,
  search,
  page,
  perPage,
}: {
  realmId: string;
  leagueId: string;
  category: string;
  referenceCurrency: string;
  search: string;
  page: number;
  perPage: number;
}) {
  return <></>;
}
