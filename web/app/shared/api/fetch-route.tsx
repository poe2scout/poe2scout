import * as changeKeys from "change-case/keys";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "");

function resolveRoute(route: string) {
  if (!apiBaseUrl || /^[a-z][a-z0-9+.-]*:\/\//i.test(route)) {
    return route;
  }

  const canonicalPath = route.replace(/^\/api(?=\/|$)/, "") || "/";
  return `${apiBaseUrl}${canonicalPath}`;
}

export default async function fetchRoute(route: string) {
  const response = await fetch(resolveRoute(route));

  if (!response.ok) {
    throw new Response("API request failed", {
      status: response.status,
      statusText: response.statusText,
    });
  }

  return changeKeys.camelCase(await response.json(), 10);
}
