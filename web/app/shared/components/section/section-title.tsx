export default function SectionTitle({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <h2 className="text-lg font-semibold tracking-tight text-white">
      {children}
    </h2>
  );
}
