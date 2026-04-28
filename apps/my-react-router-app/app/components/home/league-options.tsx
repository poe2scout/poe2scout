import useLeagues from "~/api/use-leagues";
import type Realm from "~/types/realm";
import NavLinkButton from "./nav-link-button";

export default function LeagueOptions({ realm }: { realm: Realm }) {
  const { data, isLoading } = useLeagues(realm.realmApiId);

  if (isLoading) {
    return <span>Loading...</span>;
  }

  return (
    <>
      <span className="text-2xl">Select your league</span>
      <div className="mt-2.5 grid w-full grid-cols-1 gap-2.5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {data &&
          data.map((league) => {
            return (
              <NavLinkButton
                route={`${realm.realmApiId}/${league.value}/economy`}
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
