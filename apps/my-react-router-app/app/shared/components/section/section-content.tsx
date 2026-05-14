export default function SectionContent({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="my-3 p-1.5">{children}</div>;
}
