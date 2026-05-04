import { Outlet, useLoaderData } from "react-router";
import { queryClient } from "~/api/query-client";
import getCategoriesQueryOptions from "~/api/query-options/categories";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";
import type { Route } from "./+types";
import { useLeagueContext } from "~/contexts/league-context";

type itemType = "currency" | "unique";

type category = {
  apiId: string;
  categoryId: number;
  icon: string;
  label: string;
  type: itemType;
};

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: params.category,
  }),
};

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  let categories;
  try {
    categories = await queryClient.ensureQueryData(
      getCategoriesQueryOptions(params.realmId, params.leagueId),
    );
  } catch {
    throw new Response("Invalid category", { status: 404 });
  }

  const currencyCategory = categories.currencyCategories.find((cc) => {
    return cc.apiId === params.category;
  });

  const uniqueCategory = categories.uniqueCategories.find((uc) => {
    return uc.apiId === params.category;
  });

  if (currencyCategory) {
    return {
      apiId: currencyCategory.apiId,
      categoryId: currencyCategory.currencyCategoryId,
      icon: currencyCategory.icon,
      label: currencyCategory.label,
      type: "currency",
    } as category;
  }

  if (uniqueCategory) {
    return {
      apiId: uniqueCategory.apiId,
      categoryId: uniqueCategory.itemCategoryId,
      icon: uniqueCategory.icon,
      label: uniqueCategory.label,
      type: "unique",
    } as category;
  }

  throw new Response("Invalid category", { status: 404 });
}

export default function CategoryLayout() {
  const loaderData = useLoaderData<typeof clientLoader>();

  return <Outlet context={{ loaderData }} />;
}
