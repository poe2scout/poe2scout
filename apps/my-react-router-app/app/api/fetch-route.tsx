import * as changeKeys from "change-case/keys";

export default async function fetchRoute(route: string) {
  const response = await fetch(route);
  return changeKeys.camelCase(await response.json(), 10);
}
