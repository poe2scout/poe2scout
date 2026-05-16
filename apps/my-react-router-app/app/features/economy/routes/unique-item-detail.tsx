import type { Route } from "./+types/unique-item-detail";
import { useMemo } from "react";
import { useLocation, useSearchParams } from "react-router";
import getItemQueryOptions from "../queries/item";
import { getChartMode } from "../components/item-history-charts";
import { useLeagueContext } from "~/features/league/context";
import { queryClient } from "~/shared/api/query-client";
import type { BreadcrumbHandle } from "~/features/app-shell/components/header-breadcrumbs";
import ItemDetail from "../components/item-detail";
import getLeaguesQueryOptions from "~/features/league/queries/leagues";
import getReferenceCurrenciesQueryOptions from "~/features/league/queries/reference-currencies";

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
  const referenceCurrencyParam = url.searchParams.get("referenceCurrency");

  if (!Number.isFinite(itemId)) {
    throw new Response("Invalid item", { status: 404 });
  }

  const [item, leagues, referenceCurrencies] = await Promise.all([
    queryClient.fetchQuery(
      getItemQueryOptions({
        realmApiId: params.realmId,
        leagueName: params.leagueId,
        itemId,
      }),
    ),
    queryClient.fetchQuery(getLeaguesQueryOptions(params.realmId)),
    queryClient.fetchQuery(
      getReferenceCurrenciesQueryOptions(params.realmId, params.leagueId),
    ),
  ]);

  const league = leagues.find((league) => league.value === params.leagueId);

  if (!item) {
    throw new Response("Invalid item", { status: 404 });
  }

  if (!league) {
    throw new Response("Invalid league", { status: 404 });
  }

  const referenceCurrency =
    referenceCurrencyParam ?? league.defaultCurrency.apiId;

  return { item, chartMode, referenceCurrency, referenceCurrencies };
}

export default function UniqueItemDetail({
  params,
  loaderData,
}: Route.ComponentProps) {
  const routeKind = "uniques";
  const location = useLocation();
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
    setSearchParams(nextParams, {
      preventScrollReset: true,
      replace: true,
      state: location.state,
    });
  };

  return (
    <ItemDetail
      item={loaderData.item}
      routeKind={routeKind}
      chartMode={loaderData.chartMode}
      referenceCurrency={loaderData.referenceCurrency}
      referenceCurrencies={loaderData.referenceCurrencies}
      league={league}
      realm={realm}
      backTo={backTo}
      setDetailParam={setDetailParam}
    />
  );
}
