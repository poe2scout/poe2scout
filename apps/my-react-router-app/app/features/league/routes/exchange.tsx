import type { BreadcrumbHandle } from "~/features/app-shell/components/header-breadcrumbs";
import type { Route } from "./+types/exchange";

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
