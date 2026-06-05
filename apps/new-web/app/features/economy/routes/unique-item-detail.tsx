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
import { findLeagueByRouteId } from "~/features/league/route-id";
import getReferenceCurrenciesQueryOptions from "~/features/league/queries/reference-currencies";
import {
  createPageMeta,
  formatTitle,
  getItemTitle,
  getLeagueContextTitle,
} from "~/shared/meta/page-title";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ data, params }) => ({
    label: getItemBreadcrumbLabel(data, params.itemName),
  }),
};

export function meta({ loaderData, matches }: Route.MetaArgs) {
  const itemTitle = getItemTitle(loaderData?.item);
  const leagueContext = getLeagueContextTitle(matches);
  const title = formatTitle([`${itemTitle} Price History`, leagueContext]);
  const context = leagueContext ?? "the selected league";

  return createPageMeta({
    title,
    description: `View ${itemTitle} price history, unique item value trends, and Path of Exile 2 market data for ${context}.`,
  });
}

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

  const league = findLeagueByRouteId(leagues, params.leagueId);

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

function getItemBreadcrumbLabel(data: unknown, itemName: string | undefined) {
  const itemTitle = getItemTitle(
    data && typeof data === "object" && "item" in data
      ? (data as { item?: Parameters<typeof getItemTitle>[0] }).item
      : undefined,
  );

  if (itemTitle !== "Item") {
    return itemTitle;
  }

  return itemName ? decodeItemSlug(itemName) : "Item";
}

function decodeItemSlug(itemName: string) {
  try {
    return decodeURIComponent(itemName).replaceAll("-", " ");
  } catch {
    return itemName.replaceAll("-", " ");
  }
}
