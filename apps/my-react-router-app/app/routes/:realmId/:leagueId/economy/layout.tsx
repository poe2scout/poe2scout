import { NavLink, useOutletContext, useParams } from "react-router";
import { Outlet } from "react-router";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";
import { useQuery } from "@tanstack/react-query";
import getCategoriesQueryOptions from "~/api/use-categories";
import type { Route } from "./+types";
import getLeaguesQueryOptions from "~/api/use-leagues";
import Loading from "~/components/loading";
import type League from "~/types/league";
import { useLeagueContext } from "../layout";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: "Economy",
    to: `/${params.realmId}/${params.leagueId}/economy`,
  }),
};

export default function LeagueLayout({ params }: Route.ComponentProps) {
  const { league } = useLeagueContext();

  const { data, isPending } = useQuery({
    ...getCategoriesQueryOptions(params.realmId, league.value),
  });

  if (isPending) {
    return <Loading />;
  }

  return (
    <div>
      <nav className="flex w-57.5 flex-col">
        {data?.currencyCategories.map((category) => {
          return (
            <NavLink className="w-full text-sm" to={`${category.label}`}>
              {category.label}
            </NavLink>
          );
        })}
        {data?.uniqueCategories.map((category) => {
          return (
            <NavLink className="w-full text-sm" to={`${category.label}`}>
              {category.label}
            </NavLink>
          );
        })}
      </nav>
      <div>
        <Outlet />
      </div>
    </div>
  );
}
