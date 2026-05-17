import type { Route } from "./+types/index";
import NavLinkButton from "~/features/landing/components/nav-link-button";
import { useLeagueContext } from "~/features/league/context";
import useCurrentGame from "~/features/league/hooks/use-current-game";
import Section from "~/shared/components/section/section";
import { formatTitle, getLeagueContextTitle } from "~/shared/meta/page-title";

export function meta({ matches }: Route.MetaArgs) {
  const leagueContext = getLeagueContextTitle(matches);

  return [{ title: formatTitle(["Overview", leagueContext]) }];
}

export default function Index() {
  const gameId = useCurrentGame();
  const { league, realm } = useLeagueContext();

  return (
    <div className="flex w-full flex-col gap-4 py-4">
      <Section>
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-white">
              {league.value} Overview
            </h1>
            <p className="mt-1 text-sm text-white/60">
              {realm.realmApiId} market tools and price data.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <NavLinkButton route="./economy">Economy</NavLinkButton>
            <NavLinkButton route="./exchange" filled={false}>
              Currency Exchange
            </NavLinkButton>
          </div>
        </div>
      </Section>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <FeaturePanel
          title="Economy"
          description="Browse item categories, search by item type, and inspect current prices with historical context."
          route="./economy"
          action="Open economy"
        />
        <FeaturePanel
          title="Currency Exchange"
          description="Review market volume, exchange rates, pair history, and recent market movement."
          route="./exchange"
          action="Open exchange"
          filled={false}
        />
        {gameId === 2 && (
          <FeaturePanel
            title="Unique Items"
            description="Find priced unique item categories from the economy search and category navigation."
            route="./economy/uniques/accessory"
            action="Browse uniques"
            filled={false}
          />
        )}
      </div>
    </div>
  );
}

function FeaturePanel({
  title,
  description,
  route,
  action,
  filled = true,
}: {
  title: string;
  description: string;
  route: string;
  action: string;
  filled?: boolean;
}) {
  return (
    <Section className="flex h-full flex-col">
      <div className="flex flex-1 flex-col">
        <h2 className="text-lg font-semibold text-white">{title}</h2>
        <p className="mt-2 flex-1 text-sm leading-6 text-white/60">
          {description}
        </p>
        <div className="mt-4">
          <NavLinkButton route={route} filled={filled}>
            {action}
          </NavLinkButton>
        </div>
      </div>
    </Section>
  );
}
