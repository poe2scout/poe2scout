import type { BreadcrumbHandle } from "~/components/layout/header-breadcrumbs";
import type { Route } from "./+types";
import { redirect } from "react-router";

export async function clientLoader({ params }: Route.LoaderArgs) {}

export default function Economy({ params }: Route.ComponentProps) {
  return <></>;
}
