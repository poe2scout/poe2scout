import type Realm from "~/types/realm";
import NavLinkButton from "./nav-link-button";
import Loading from "../loading";
import getLeaguesQueryOptions from "~/api/use-leagues";
import { useQuery } from "@tanstack/react-query";

export default function LeagueOptions({ realm }: { realm: Realm }) {
  const { data, isPending } = useQuery(
    getLeaguesQueryOptions(realm.realmApiId),
  );

  if (isPending) return <Loading />;

  return (
    <>
      <span className="text-2xl">Select your league</span>
      <div className="mt-2.5 grid w-full grid-cols-1 gap-2.5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {data &&
          data.map((league) => {
            return (
              <NavLinkButton
                route={`${realm.realmApiId}/${league.value}`}
                key={league.value}
              >
                {league.value}
              </NavLinkButton>
            );
          })}
      </div>
    </>
  );
}
