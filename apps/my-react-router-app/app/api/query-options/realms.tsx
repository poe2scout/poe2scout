import { queryOptions } from "@tanstack/react-query";
import type Realm from "~/types/realm";
import fetchRoute from "../fetch-route";

export default function getRealmsQueryOptions() {
  return queryOptions({
    queryKey: ["realms"],
    queryFn: async () =>
      (await fetchRoute(`/api/Static/Realms`)) as Promise<Realm[]>,
  });
}
