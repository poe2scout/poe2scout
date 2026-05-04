import type Realm from "~/types/realm";
import NavLinkButton from "./nav-link-button";
import Loading from "../loading";
import getLeaguesQueryOptions from "~/api/query-options/leagues";
import { useQuery } from "@tanstack/react-query";
import SectionTitle from "../section-title";
import SectionDivider from "../section-divider";
import SectionContent from "../section-content";

export default function LeagueOptions({ realm }: { realm: Realm }) {
  const { data, isPending } = useQuery(
    getLeaguesQueryOptions(realm.realmApiId),
  );

  if (isPending) return <Loading />;

  const currentLeagues = data?.filter((l) => {
    return l.isCurrent;
  });

  const inactiveLeagues = data?.filter((l) => {
    return !l.isCurrent;
  });

  return (
    <>
      <SectionTitle>Select a League</SectionTitle>
      <SectionDivider />
      <SectionContent>
        <div className="flex flex-col items-center">
          <span className="mb-3">Active</span>
          <div className="grid w-full grid-cols-1 gap-2.5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {currentLeagues &&
              currentLeagues.map((league) => {
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
          <span className="mt-6 mb-3">Past</span>
          <div className="grid w-full grid-cols-1 gap-2.5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {inactiveLeagues &&
              inactiveLeagues.map((league) => {
                return (
                  <NavLinkButton
                    route={`${realm.realmApiId}/${league.value}`}
                    key={league.value}
                    filled={false}
                  >
                    {league.value}
                  </NavLinkButton>
                );
              })}
          </div>
        </div>
      </SectionContent>
    </>
  );
}
