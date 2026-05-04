import { NavLink } from "react-router";
import { Outlet } from "react-router";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";
import {
  usePrefetchQuery,
  useQuery,
  useSuspenseQuery,
} from "@tanstack/react-query";
import getCategoriesQueryOptions from "~/api/query-options/categories";
import type { Route } from "./+types";
import Loading from "~/components/loading";
import ItemSearch from "~/components/economy/item-search";
import { useLeagueContext } from "~/contexts/league-context";
import { queryClient } from "~/api/query-client";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: "Economy",
    to: `/${params.realmId}/${params.leagueId}/economy`,
  }),
};

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  await queryClient.prefetchQuery(
    getCategoriesQueryOptions(params.realmId, params.leagueId),
  );
}

export default function EconomyLayout({ params }: Route.ComponentProps) {
  const { league } = useLeagueContext();
  const { data } = useSuspenseQuery(
    getCategoriesQueryOptions(params.realmId, league.value),
  );

  return (
    <div>
      <div className="flex flex-row justify-between">
        <nav className="m-3 flex w-57.5 flex-col overflow-hidden rounded-sm border border-secondary/35 bg-zinc-950 shadow-lg shadow-black/30">
          <span className="px-3 py-2 text-sm text-white/70">
            Currency categories
          </span>
          {data?.currencyCategories.map((category) => {
            return (
              <NavLink
                className={({ isActive }) =>
                  `flex w-full justify-between px-3 py-2 text-sm transition outline-none hover:bg-secondary/20 focus:bg-secondary/25 ${
                    isActive ? "bg-secondary/30 text-white" : "text-white/80"
                  }`
                }
                to={`currencies/${category.apiId}`}
                end
                key={category.label}
              >
                <img
                  className="h-6 w-6"
                  src={category.icon !== "" ? category.icon : undefined}
                ></img>
                <span className="w-35.25">{category.label}</span>
              </NavLink>
            );
          })}
          {data?.uniqueCategories.length !== 0 && (
            <span className="border-t border-secondary/20 px-3 py-2 text-sm text-white/70">
              Unique categories
            </span>
          )}

          {data?.uniqueCategories.map((category) => {
            return (
              <NavLink
                className={({ isActive }) =>
                  `flex w-full justify-between px-3 py-2 text-sm transition outline-none hover:bg-secondary/20 focus:bg-secondary/25 ${
                    isActive ? "bg-secondary/30 text-white" : "text-white/80"
                  }`
                }
                to={`uniques/${category.apiId}`}
                end
                key={category.label}
              >
                <img
                  className="h-6 w-6"
                  src={category.icon !== "" ? category.icon : undefined}
                ></img>
                <span className="w-35.25">{category.label}</span>
              </NavLink>
            );
          })}
        </nav>
        <div className="flex-1">
          <div>
            <ItemSearch realmId={params.realmId}></ItemSearch>
          </div>
          <Outlet />
        </div>
      </div>
    </div>
  );
}
