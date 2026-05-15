import * as changeKeys from "change-case/keys";

export default async function fetchRoute(route: string) {
  const response = await fetch(route);

  if (!response.ok) {
    throw new Response("API request failed", {
      status: response.status,
      statusText: response.statusText,
    });
  }

  return changeKeys.camelCase(await response.json(), 10);
}
