import type { Route } from "./+types/exchange";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";

export const handle: BreadcrumbHandle = {
  breadcrumb: () => ({ label: "Currency Exchange" }),
};

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  const response = await fetch(`/api/${params.realmId}/Leagues`);
  console.log(response);
}

export default function Exchange() {
  return <></>;
}
