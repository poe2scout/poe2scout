import Section from "~/components/section";
import SectionTitle from "~/components/section-title";
import SectionDivider from "~/components/section-divider";
import SectionContent from "~/components/section-content";

export default function Economy() {
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
