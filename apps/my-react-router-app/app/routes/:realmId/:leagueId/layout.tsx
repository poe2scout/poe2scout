import { Outlet, useLoaderData } from "react-router";
import getLeaguesQueryOptions from "~/api/query-options/leagues";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";
import type { Route } from "./+types";
import { queryClient } from "~/api/query-client";
import { LeagueContext } from "~/contexts/league-context";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: "Home",
    to: `/${params.realmId}/${params.leagueId}`,
  }),
};

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  let leagues;
  try {
    leagues = await queryClient.ensureQueryData(
      getLeaguesQueryOptions(params.realmId),
    );
  } catch {
    throw new Response("Invalid realm", { status: 404 });
  }

  const league = leagues.find((l) => l.value === params.leagueId);

  if (!league) {
    throw new Response("Invalid league", { status: 404 });
  }

  return { league };
}

export default function LeagueLayout() {
  const loaderData = useLoaderData<typeof clientLoader>();

  return (
    <LeagueContext.Provider value={{ league: loaderData.league }}>
      <Outlet />
    </LeagueContext.Provider>
  );
}
