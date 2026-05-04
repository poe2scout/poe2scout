import type { Route } from "./+types";
import NavLinkButton from "~/components/home/nav-link-button";
import SectionTitle from "~/components/section-title";
import Section from "~/components/section";
import useCurrentGame from "~/hooks/use-current-game";
import SectionContent from "~/components/section-content";
import SectionDivider from "~/components/section-divider";

export default function Index({ params }: Route.ComponentProps) {
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
