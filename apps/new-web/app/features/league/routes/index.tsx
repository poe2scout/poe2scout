import type { Route } from "./+types/index";
import NavLinkButton from "~/features/landing/components/nav-link-button";
import useCurrentGame from "~/features/league/hooks/use-current-game";
import Section from "~/shared/components/section/section";
import SectionContent from "~/shared/components/section/section-content";
import SectionDivider from "~/shared/components/section/section-divider";
import SectionTitle from "~/shared/components/section/section-title";
import {
  formatTitle,
  getLeagueContextTitle,
} from "~/shared/meta/page-title";

export function meta({ matches }: Route.MetaArgs) {
  const leagueContext = getLeagueContextTitle(matches);

  return [{ title: formatTitle(["Overview", leagueContext]) }];
}

export default function Index() {
  const gameId = useCurrentGame();

  return (
    <div className="flex w-full flex-col items-center">
      <Section>
        <SectionTitle>Currency Item Overview</SectionTitle>
        <SectionDivider />
        <img
          className="w-2/5"
          src="/ItemOverview.png"
          alt="Image of currency item overview page"
        />
        <SectionContent>
          <div className="flex flex-col items-center gap-3">
            {"See hourly price snapshots of currency item prices.\n" +
              "Analyse historical data with different chart types."}
            <NavLinkButton route="./economy">Economy</NavLinkButton>
          </div>
        </SectionContent>
      </Section>
      {gameId === 2 && (
        <Section>
          <SectionTitle>Unique Item Overview</SectionTitle>
          <img
            className="w-2/5"
            src="/ItemOverview.png"
            alt="Image of currency item overview page"
          />
        </Section>
      )}
      <Section>
        <SectionTitle>Currency Exchange Explorer</SectionTitle>
        <SectionDivider />
        <img
          className="w-2/5"
          src="/ItemOverview.png"
          alt="Image of currency item overview page"
        />
        <SectionContent>
          <div className="flex flex-col items-center gap-3">
            <span>
              {"See hourly price snapshots of currency item prices.\n" +
                "Analyse historical data with different chart types."}
            </span>
            <NavLinkButton route="./exchange">
              Currency exchange explorer
            </NavLinkButton>
          </div>
        </SectionContent>
      </Section>
    </div>
  );
}
