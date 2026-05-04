import Section from "~/components/section";
import type { Route } from "./+types";
import SectionTitle from "~/components/section-title";
import SectionDivider from "~/components/section-divider";
import SectionContent from "~/components/section-content";

export async function clientLoader({ params }: Route.LoaderArgs) {}

export default function Economy({ params }: Route.ComponentProps) {
  return (
    <>
      <Section>
        <SectionTitle>Welcome to the economy overview</SectionTitle>
        <SectionDivider />
        <SectionContent>
          Select a category on the left to get started or search for an item
          above.
        </SectionContent>
      </Section>
    </>
  );
}
