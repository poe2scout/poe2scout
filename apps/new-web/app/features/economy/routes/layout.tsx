import { NavLink, Outlet, useLocation, useNavigate } from "react-router";
import { queryClient } from "~/shared/api/query-client";
import type { BreadcrumbHandle } from "~/features/app-shell/components/header-breadcrumbs";
import getCategoriesQueryOptions from "../queries/categories";
import type { Route } from "./+types/layout";
import ItemSearch from "../components/item-search";
import { formatTitle, getLeagueContextTitle } from "~/shared/meta/page-title";
import type { Filter } from "../queries/filters";
import ResponsiveAdLayout from "~/shared/components/ads/responsive-ad-layout";

const routeKindByItemKind: Record<
  Filter["itemKind"],
  "currencies" | "uniques"
> = {
  currency: "currencies",
  unique: "uniques",
};

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: "Economy",
    to: `/${params.realmId}/${params.leagueId}/economy`,
  }),
};

export function meta({ matches }: Route.MetaArgs) {
  const leagueContext = getLeagueContextTitle(matches);

  return [{ title: formatTitle(["Economy", leagueContext]) }];
}

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  return queryClient.fetchQuery(
    getCategoriesQueryOptions(params.realmId, params.leagueId),
  );
}

export default function EconomyLayout({
  params,
  loaderData,
}: Route.ComponentProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const basePath = `/${params.realmId}/${params.leagueId}/economy`;
  const currentSearchParams = new URLSearchParams(location.search);
  const activeSearchValue = currentSearchParams.get("search") ?? "";
  const currencyCategoryOptions = loaderData.currencyCategories.map(
    (category) => ({
      ...category,
      type: "currencies" as const,
      value: `currencies/${category.apiId}`,
    }),
  );
  const uniqueCategoryOptions = loaderData.uniqueCategories.map((category) => ({
    ...category,
    type: "uniques" as const,
    value: `uniques/${category.apiId}`,
  }));
  const categoryOptions = [
    ...currencyCategoryOptions,
    ...uniqueCategoryOptions,
  ];
  const currentCategoryValue =
    categoryOptions.find((category) => {
      const categoryPath = `${basePath}/${category.value}`;

      return (
        location.pathname === categoryPath ||
        location.pathname.startsWith(`${categoryPath}/`)
      );
    })?.value ?? "";

  const handleCategoryChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
  ) => {
    const nextCategory = event.currentTarget.value;

    if (nextCategory) {
      navigate(`${basePath}/${nextCategory}`);
    }
  };

  const handleSearchFilterSelect = (filter: Filter) => {
    const routeKind = routeKindByItemKind[filter.itemKind];
    const nextSearchParams = new URLSearchParams();
    const referenceCurrency = currentSearchParams.get("referenceCurrency");

    nextSearchParams.set("search", filter.identifier);

    if (referenceCurrency) {
      nextSearchParams.set("referenceCurrency", referenceCurrency);
    }

    navigate(
      `${basePath}/${routeKind}/${encodeURIComponent(filter.category)}?${nextSearchParams.toString()}`,
    );
  };

  const handleSearchFilterRemove = () => {
    const nextSearchParams = new URLSearchParams(location.search);
    nextSearchParams.delete("search");
    nextSearchParams.delete("page");
    nextSearchParams.delete("perPage");

    const query = nextSearchParams.toString();
    navigate(`${location.pathname}${query ? `?${query}` : ""}`);
  };

  return (
    <ResponsiveAdLayout>
      <div className="mb-3">
        <ItemSearch
          realmId={params.realmId}
          activeSearchValue={activeSearchValue}
          onFilterSelect={handleSearchFilterSelect}
          onSearchFilterRemove={handleSearchFilterRemove}
        ></ItemSearch>
      </div>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start">
        <nav className="hidden w-57.5 shrink-0 flex-col overflow-hidden rounded-sm border border-secondary/35 bg-zinc-900 shadow-lg shadow-black/30 lg:flex">
          <NavHeader>Currency categories</NavHeader>

          {currencyCategoryOptions.map((category) => {
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
          {uniqueCategoryOptions.length !== 0 && (
            <NavHeader>Unique categories</NavHeader>
          )}

          {uniqueCategoryOptions.map((category) => {
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
        <div className="lg:hidden">
          <label className="sr-only" htmlFor="economy-category-select">
            Economy category
          </label>
          <select
            id="economy-category-select"
            value={currentCategoryValue}
            onChange={handleCategoryChange}
            className="h-10 w-full rounded-sm border border-secondary/35 bg-zinc-900 px-3 text-sm text-white shadow-lg shadow-black/30 outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/25"
          >
            <option value="">Select category</option>
            <optgroup label="Currency categories">
              {currencyCategoryOptions.map((category) => (
                <option key={category.apiId} value={category.value}>
                  {category.label}
                </option>
              ))}
            </optgroup>
            {uniqueCategoryOptions.length !== 0 && (
              <optgroup label="Unique categories">
                {uniqueCategoryOptions.map((category) => (
                  <option key={category.apiId} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </optgroup>
            )}
          </select>
        </div>
        <div className="min-w-0 flex-1">
          <Outlet />
        </div>
      </div>
    </ResponsiveAdLayout>
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
