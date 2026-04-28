import { useQuery } from "@tanstack/react-query";
import type Realm from "~/types/realm";
import * as changeKeys from "change-case/keys";

async function FetchRealms(): Promise<Realm[]> {
  const response = await fetch("api/Static/Realms");
  return changeKeys.camelCase(await response.json(), 10) as Realm[];
}

export default function useRealms() {
  return useQuery({
    queryKey: ["realms"],
    queryFn: FetchRealms,
  });
}
