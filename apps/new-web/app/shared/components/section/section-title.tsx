export default function SectionTitle({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <h2 className="mb-1.5 text-center text-3xl font-semibold tracking-tight text-white">
      {children}
    </h2>
  );
}
