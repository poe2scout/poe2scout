import type { Route } from "./+types";

export async function clientLoader({ params }: Route.LoaderArgs) {
  const response = await fetch(`/api/${params.realmId}/Leagues`);
  console.log(response);
}

export default function Economy({ params }: Route.ComponentProps) {
  return <></>;
}
