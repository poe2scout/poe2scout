import { NavLink } from "react-router";

export default function NavLinkButton({
  route,
  children,
  filled = true,
}: {
  route: string;
  children: React.ReactNode;
  filled?: boolean;
}) {
  return (
    <NavLink
      to={route}
      prefetch="intent"
      className={`inline-flex min-h-10 items-center justify-between gap-2 rounded-sm border border-secondary/35 px-3 py-2 text-sm transition outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/25 ${"bg-transparent text-white/80 hover:bg-secondary/10 hover:text-white"}`}
    >
      <span className="truncate">{children}</span>
      <span aria-hidden="true" className="shrink-0 leading-none font-normal">
        &rarr;
      </span>
    </NavLink>
  );
}
