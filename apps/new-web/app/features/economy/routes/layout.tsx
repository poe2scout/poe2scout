import { NavLink } from "react-router";
import { Outlet } from "react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useLeagueContext } from "~/features/league/context";
import { queryClient } from "~/shared/api/query-client";
import type { BreadcrumbHandle } from "~/features/app-shell/components/header-breadcrumbs";
import getCategoriesQueryOptions from "../queries/categories";
import type { Route } from "./+types/layout";
import ItemSearch from "../components/item-search";

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
      <div className="mb-3">
        <ItemSearch realmId={params.realmId}></ItemSearch>
      </div>
      <div className="flex flex-row items-start justify-between gap-3">
        <nav className="flex w-57.5 flex-col overflow-hidden rounded-sm border border-secondary/35 bg-zinc-950 shadow-lg shadow-black/30">
          <NavHeader>Currency categories</NavHeader>

          {data?.currencyCategories.map((category) => {
            return (
              <NavItem
                key={category.apiId}
                apiId={category.apiId}
                label={category.label}
                icon={category.icon}
                type="currencies"
              />
            );
          })}
          {data?.uniqueCategories.length !== 0 && (
            <NavHeader>Unique categories</NavHeader>
          )}

          {data?.uniqueCategories.map((category) => {
            return (
              <NavItem
                key={category.apiId}
                apiId={category.apiId}
                label={category.label}
                icon={category.icon}
                type="uniques"
              />
            );
          })}
        </nav>
        <div className="flex-1">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

function NavHeader({ children }: { children: React.ReactNode }) {
  return (
    <span className="border-t border-secondary/20 px-3 py-2 text-sm text-white/70">
      {children}
    </span>
  );
}

function NavItem({
  apiId,
  label,
  type,
  icon,
}: {
  apiId: string;
  label: string;
  type: string;
  icon: string;
}) {
  return (
    <NavLink
      className={({ isActive }) =>
        `flex w-full justify-between px-3 py-2 text-sm transition outline-none hover:bg-secondary/20 focus:bg-secondary/25 ${isActive ? "bg-secondary/30 text-white" : "text-white/80"}`
      }
      to={`${type}/${apiId}`}
      end
      key={label}
      prefetch="intent"
    >
      <img className="h-6 w-6" src={icon !== "" ? icon : undefined}></img>
      <span className="w-35.25">{label}</span>
    </NavLink>
  );
}
