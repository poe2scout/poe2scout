import type { Route } from "./+types";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";

export const handle: BreadcrumbHandle = {
  breadcrumb: () => ({ label: "Currency Exchange" }),
};

export async function clientLoader({ params }: Route.LoaderArgs) {
  const response = await fetch(`/api/${params.realmId}/Leagues`);
  console.log(response);
}

export default function Exchange({ params }: Route.ComponentProps) {
  return <></>;
}
