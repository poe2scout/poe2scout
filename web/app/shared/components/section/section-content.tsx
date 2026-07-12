export default function SectionContent({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="mt-3 text-sm text-white/70">{children}</div>;
}
