import { Outlet, useLoaderData, useOutletContext } from "react-router";
import getLeaguesQueryOptions from "~/api/use-leagues";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";
import { queryClient } from "~/root";
import type { Route } from "./+types";
import type Realm from "~/types/realm";
import type League from "~/types/league";

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

export function useLeagueContext() {
  return useOutletContext<{ league: League }>();
}

export default function LeagueLayout({ params }: Route.ComponentProps) {
  const loaderData = useLoaderData<typeof clientLoader>();
  return <Outlet context={{ league: loaderData.league }} />;
}
