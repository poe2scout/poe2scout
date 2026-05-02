import { Outlet } from "react-router";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: "Economy",
    to: `/${params.realmId}/${params.leagueId}/economy`,
  }),
};

export default function LeagueLayout() {
  return <Outlet />;
}
