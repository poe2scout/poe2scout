import { Outlet } from "react-router";
import { queryClient } from "~/shared/api/query-client";
import { LeagueContext } from "~/features/league/context";
import type { BreadcrumbHandle } from "~/features/app-shell/components/header-breadcrumbs";
import getLeaguesQueryOptions from "../queries/leagues";
import type { Route } from "./+types/layout";
import getRealmsQueryOptions from "../queries/realms";

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
