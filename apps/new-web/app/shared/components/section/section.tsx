import type { ReactNode } from "react";

export default function Section({ children }: { children: ReactNode }) {
  return (
    <section className="mt-3 flex w-full flex-col items-center rounded-lg bg-gray-900 py-6">
      {children}
    </section>
  );
}
