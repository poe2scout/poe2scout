import type { Route } from "./+types/unique-item-detail";
import { useMemo } from "react";
import { useSearchParams } from "react-router";
import getItemsQueryOptions from "../queries/items";
import { getChartMode } from "../components/item-history-charts";
import { useLeagueContext } from "~/features/league/context";
import { queryClient } from "~/shared/api/query-client";
import type { BreadcrumbHandle } from "~/features/app-shell/components/header-breadcrumbs";
import ItemDetail from "../components/item-detail";

export const handle: BreadcrumbHandle = {
  breadcrumb: () => ({
    label: "Item",
  }),
};

export async function clientLoader({
  request,
  params,
}: Route.ClientLoaderArgs) {
  const itemId = Number(params.itemId);
  const url = new URL(request.url);

  const chartMode = getChartMode(url.searchParams.get("chart"));
  const referenceCurrency = url.searchParams.get("referenceCurrency");

  const items = await queryClient.fetchQuery(
    getItemsQueryOptions({
      realmApiId: params.realmId,
      leagueName: params.leagueId,
    }),
  );

  const item = items.find((item) => item.itemId === itemId);

  if (!item) {
    throw new Response("Invalid item", { status: 404 });
  }

  return { item, chartMode, referenceCurrency };
}

export default function UniqueItemDetail({
  params,
  loaderData,
}: Route.ComponentProps) {
  const routeKind = "uniques";
  const [searchParams, setSearchParams] = useSearchParams();
  const { league, realm } = useLeagueContext();

  const backTo = useMemo(() => {
    const nextParams = new URLSearchParams(searchParams);
    nextParams.delete("chart");
    const query = nextParams.toString();

    return `/${params.realmId}/${params.leagueId}/economy/${routeKind}/${params.category}${query ? `?${query}` : ""}`;
  }, [
    params.category,
    params.leagueId,
    params.realmId,
    routeKind,
    searchParams,
  ]);

  const setDetailParam = (key: string, value: string) => {
    const nextParams = new URLSearchParams(searchParams);
    nextParams.set(key, value);
    setSearchParams(nextParams);
  };

  return (
    <ItemDetail
      item={loaderData.item}
      routeKind={routeKind}
      chartMode={loaderData.chartMode}
      referenceCurrency={
        loaderData.referenceCurrency ?? league.defaultCurrency.apiId
      }
      league={league}
      realm={realm}
      backTo={backTo}
      setDetailParam={setDetailParam}
    />
  );
}
