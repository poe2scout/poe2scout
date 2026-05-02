import { Outlet } from "react-router";
import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: "Home",
    to: `/${params.realmId}/${params.leagueId}`,
  }),
};

export default function LeagueLayout() {
  return <Outlet />;
}
