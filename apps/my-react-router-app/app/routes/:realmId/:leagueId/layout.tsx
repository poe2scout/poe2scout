import { Outlet } from "react-router";
import getLeaguesQueryOptions from "~/api/query-options/leagues";
import getRealmsQueryOptions from "~/api/query-options/realms";
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
  const [leagues, realms] = await Promise.all([
    queryClient.fetchQuery(getLeaguesQueryOptions(params.realmId)),
    queryClient.fetchQuery(getRealmsQueryOptions()),
  ]);

  const league = leagues.find((l) => l.value === params.leagueId);
  const realm = realms.find((r) => r.realmApiId === params.realmId);

  if (!league) {
    throw new Response("Invalid league", { status: 404 });
  }

  if (!realm) {
    throw new Response("Invalid realm", { status: 404 });
  }

  return { league, realm };
}

export default function LeagueLayout({ loaderData }: Route.ComponentProps) {
  return (
    <LeagueContext.Provider
      value={{ league: loaderData.league, realm: loaderData.realm }}
    >
      <Outlet />
    </LeagueContext.Provider>
  );
}
