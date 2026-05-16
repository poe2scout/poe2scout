import { useQuery } from "@tanstack/react-query";
import getLeaguesQueryOptions from "~/features/league/queries/leagues";
import { getLeagueRouteId } from "~/features/league/route-id";
import type { Realm } from "~/features/league/types";
import Loading from "~/shared/components/loading";
import SectionDivider from "~/shared/components/section/section-divider";
import SectionTitle from "~/shared/components/section/section-title";
import NavLinkButton from "./nav-link-button";

export default function LeagueOptions({ realm }: { realm: Realm }) {
  const { data, isPending } = useQuery(
    getLeaguesQueryOptions(realm.realmApiId),
  );

  if (isPending) {
    return (
      <div className="flex min-h-28 items-center justify-center border-t border-secondary/25 pt-5">
        <Loading />
      </div>
    );
  }

  const currentLeagues = data?.filter((l) => {
    return l.isCurrent;
  });

  const inactiveLeagues = data?.filter((l) => {
    return !l.isCurrent;
  });

  return (
    <div className="space-y-4">
      <SectionDivider />
      <div>
        <SectionTitle>Leagues</SectionTitle>
        <p className="mt-1 text-sm text-white/55">
          Open a league to browse its current economy.
        </p>
      </div>
      <LeagueGroup title="Active">
        {currentLeagues?.map((league) => (
          <NavLinkButton
            route={`${realm.realmApiId}/${getLeagueRouteId(league)}`}
            key={league.value}
          >
            {league.value}
          </NavLinkButton>
        ))}
      </LeagueGroup>
      {inactiveLeagues && inactiveLeagues.length > 0 && (
        <LeagueGroup title="Past">
          {inactiveLeagues.map((league) => (
            <NavLinkButton
              route={`${realm.realmApiId}/${getLeagueRouteId(league)}`}
              key={league.value}
              filled={false}
            >
              {league.value}
            </NavLinkButton>
          ))}
        </LeagueGroup>
      )}
    </div>
  );
}

function LeagueGroup({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <h3 className="text-xs font-medium tracking-wide text-white/50 uppercase">
        {title}
      </h3>
      <div className="grid w-full grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {children}
      </div>
    </div>
  );
}
