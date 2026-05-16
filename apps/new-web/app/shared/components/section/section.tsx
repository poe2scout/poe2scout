import type { ReactNode } from "react";

export default function Section({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`w-full rounded-sm border border-secondary/35 bg-zinc-900 p-4 shadow-lg shadow-black/30 ${className}`}
    >
      {children}
    </section>
  );
}
