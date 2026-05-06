import { Outlet } from "react-router";
import getLeaguesQueryOptions from "~/api/query-options/leagues";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";
import { queryClient } from "~/api/query-client";
import { LeagueContext } from "~/contexts/league-context";
import type { Route } from "./+types/layout";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: "Home",
    to: `/${params.realmId}/${params.leagueId}`,
  }),
};

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  const leagues = await queryClient.fetchQuery(
    getLeaguesQueryOptions(params.realmId),
  );

  const league = leagues.find((l) => l.value === params.leagueId);

  if (!league) {
    throw new Response("Invalid league", { status: 404 });
  }

  return { league };
}

export default function LeagueLayout({ loaderData }: Route.ComponentProps) {
  return (
    <LeagueContext.Provider value={{ league: loaderData.league }}>
      <Outlet />
    </LeagueContext.Provider>
  );
}
