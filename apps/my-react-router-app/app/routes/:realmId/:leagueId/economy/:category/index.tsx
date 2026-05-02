import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";
import type { Route } from "./+types";
import { redirect } from "react-router";

export const handle: BreadcrumbHandle = {
  breadcrumb: ({ params }) => ({
    label: params.category,
  }),
};

export async function clientLoader({ params }: Route.LoaderArgs) {}

export default function Economy({ params }: Route.ComponentProps) {
  return <></>;
}
