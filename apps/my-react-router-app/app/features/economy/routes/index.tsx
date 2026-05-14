import Section from "~/shared/components/section/section";
import SectionTitle from "~/shared/components/section/section-title";
import SectionDivider from "~/shared/components/section/section-divider";
import SectionContent from "~/shared/components/section/section-content";

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
