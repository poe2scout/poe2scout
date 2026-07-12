import { queryOptions } from "@tanstack/react-query";
import type { Realm } from "../types";
import fetchRoute from "~/shared/api/fetch-route";

export default function getRealmsQueryOptions() {
  return queryOptions({
    queryKey: ["realms"],
    queryFn: async () => (await fetchRoute(`/api/Realms`)) as Promise<Realm[]>,
  });
}
